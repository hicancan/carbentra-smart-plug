"""CarbonMirror building-edge reference service.
No default broker, account, certificate or actuation. Only starts with explicit
owner configuration. The broker MUST enforce per-device certificate/topic ACLs.
"""
import argparse, json, math, re, sqlite3, ssl, time
from pathlib import Path
DEVICE = re.compile(r'^[A-Za-z0-9_-]{1,47}$')
NONCE = re.compile(r'^[0-9a-f]{32}$')
SEQ = re.compile(r'^[0-9]{1,20}$')
def reject_duplicate(pairs):
    out = {}
    for k, v in pairs:
        if k in out: raise ValueError('duplicate JSON key')
        out[k] = v
    return out

def finite_float(text):
    value=float(text)
    if not math.isfinite(value) or abs(value)>9007199254740991: raise ValueError('nonfinite or oversized number')
    return value

def bounded_int(text):
    if len(text)>17: raise ValueError('oversized integer')
    value=int(text)
    if abs(value)>9007199254740991: raise ValueError('oversized integer')
    return value

def strict_json(raw):
    if not isinstance(raw,(str,bytes,bytearray)) or len(raw)>8192: raise ValueError('invalid payload size/type')
    text=raw.decode('utf-8') if isinstance(raw,(bytes,bytearray)) else raw
    depth=0;quoted=False;escaped=False
    for ch in text:
        if quoted:
            if escaped: escaped=False
            elif ch=='\\': escaped=True
            elif ch=='"': quoted=False
        elif ch=='"': quoted=True
        elif ch in '{[':
            depth+=1
            if depth>32: raise ValueError('excessive JSON nesting')
        elif ch in '}]':
            depth-=1
            if depth<0: raise ValueError('unbalanced JSON')
    try:
        return json.loads(text,object_pairs_hook=reject_duplicate,parse_float=finite_float,
            parse_int=bounded_int,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
    except (RecursionError,OverflowError) as error:
        raise ValueError('excessive JSON structure') from error

class Edge:
    def __init__(self, database, allowed_devices):
        self.allowed = set(allowed_devices)
        if not all(DEVICE.fullmatch(d) for d in self.allowed): raise ValueError('invalid device ID')
        self.db = sqlite3.connect(database)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS telemetry(
            device TEXT, epoch TEXT, seq TEXT, received REAL, payload TEXT,
            PRIMARY KEY(device,epoch,seq))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS acknowledgements(
            device TEXT, command_id TEXT, received REAL, payload TEXT)''')
        self.db.commit()
    def accept(self, topic, payload, now=None):
        now = time.time() if now is None else now
        parts = topic.split('/')
        if len(parts) != 4 or parts[:2] != ['carbonmirror', 'v1']: raise ValueError('invalid topic')
        device, kind = parts[2:]
        if device not in self.allowed: raise ValueError('not enrolled')
        message = strict_json(payload)
        if not isinstance(message, dict): raise ValueError('object required')
        if kind == 'hello':
            nonce = message.get('clock_nonce')
            if not isinstance(nonce, str) or not NONCE.fullmatch(nonce): raise ValueError('bad nonce')
            return f'carbonmirror/v1/{device}/time', {'clock_nonce': nonce, 'unix_s': int(now)}
        if kind == 'telemetry':
            if message.get('device_id') != device: raise ValueError('identity mismatch')
            seq, epoch = message.get('sample_seq'), message.get('boot_epoch')
            if not isinstance(seq, str) or not SEQ.fullmatch(seq) or not 0 < int(seq) < 2**64: raise ValueError('bad sample sequence')
            if not isinstance(epoch, str) or not NONCE.fullmatch(epoch): raise ValueError('boot epoch required')
            for key in ['active_w','reactive_var','apparent_va','voltage_v','current_a','pf','frequency_hz','board_temperature_c','unix_s','monotonic_ms','known_forward_wh_since_boot','known_reverse_wh_since_boot','energy_uncertain_intervals','ram_buffer_dropped','command_dropped']:
                if key in message and (type(message[key]) not in (int,float) or not math.isfinite(message[key])): raise ValueError('bad measurement')
            for key in ['valid','calibrated','board_temperature_valid','desired_on','feedback_valid','output_present','voltage_absence_proven']:
                if key in message and type(message[key]) is not bool: raise ValueError('bad boolean')
            for key in ['known_forward_wh_since_boot','known_reverse_wh_since_boot','energy_uncertain_intervals','ram_buffer_dropped','command_dropped']:
                if key in message and message[key]<0: raise ValueError('negative accumulator')
            with self.db:
                self.db.execute('INSERT OR IGNORE INTO telemetry VALUES(?,?,?,?,?)',
                    (device,epoch,seq,now,json.dumps(message,ensure_ascii=False,separators=(',',':'),allow_nan=False)))
            # Durable receipt is distinct from MQTT PUBACK.
            return f'carbonmirror/v1/{device}/receipt', {'boot_epoch':epoch,'sample_seq':seq}
        if kind == 'ack':
            cid = message.get('id')
            if not isinstance(cid,str) or not DEVICE.fullmatch(cid): raise ValueError('bad command ID')
            with self.db:
                self.db.execute('INSERT INTO acknowledgements VALUES(?,?,?,?)',
                    (device,cid,now,json.dumps(message,ensure_ascii=False,allow_nan=False)))
            return None
        raise ValueError('unsupported direction')

def recommend_shedding(assets, reduction_w):
    """Dry-run plan only. Never publishes control commands or treats forecasts as savings."""
    if not math.isfinite(reduction_w) or reduction_w < 0: raise ValueError('bad goal')
    candidates = [a for a in assets if a.get('commissioned') and a.get('approved')
        and a.get('allow_mains_shed') and not a.get('critical') and a.get('fresh')
        and a.get('minimum_dwell_met') and type(a.get('active_w')) in (int,float)
        and math.isfinite(a['active_w']) and a['active_w'] > 0]
    chosen=[]; estimate=0.0
    for a in sorted(candidates,key=lambda x:(x.get('priority',100),-x['active_w'])):
        if estimate >= reduction_w: break
        chosen.append(a['device_id']);estimate+=a['active_w']
    return {'mode':'dry_run_recommendation','devices':chosen,'estimated_reduction_w':estimate,
        'unmet_goal_w':max(0,reduction_w-estimate),'measured_savings':None}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['broker','ca','certificate','key','devices','database']:p.add_argument('--'+k,required=True)
    p.add_argument('--port',type=int,default=8883);args=p.parse_args()
    import paho.mqtt.client as mqtt
    config=strict_json(Path(args.devices).read_text());edge=Edge(args.database,config['devices'])
    client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='carbonmirror-building-edge')
    client.tls_set(ca_certs=args.ca,certfile=args.certificate,keyfile=args.key,tls_version=ssl.PROTOCOL_TLS_CLIENT)
    client.tls_insecure_set(False)
    def connect(c,u,flags,reason,props):
        if reason != 0: return
        for device in edge.allowed:
            for channel in ('hello','telemetry','ack'):c.subscribe(f'carbonmirror/v1/{device}/{channel}',qos=1)
    def message(c,u,m):
        if m.retain: return
        try:
            result=edge.accept(m.topic,m.payload)
            if result:c.publish(result[0],json.dumps(result[1],separators=(',',':')),qos=1,retain=False)
        except (ValueError,UnicodeError,json.JSONDecodeError,sqlite3.Error) as error:
            print('Rejected message:',type(error).__name__) # No secrets/raw payload logs
    client.on_connect=connect;client.on_message=message
    client.connect(args.broker,args.port,keepalive=30);client.loop_forever()

# Transparent forecasting baseline for comparison before any learned model.
def forecast_baseline(samples, horizon_s=300):
    import statistics
    if not math.isfinite(horizon_s) or not 0 <= horizon_s <= 3600:
        raise ValueError('forecast horizon outside baseline scope')
    points=[]
    for s in samples[-60:]:
        t,p=s.get('unix_s'),s.get('active_w')
        if s.get('valid') is True and type(t) in (int,float) and type(p) in (int,float) and math.isfinite(t) and math.isfinite(p) and p>=0:
            points.append((float(t),float(p)))
    points=sorted(dict(points).items())
    if len(points)<12 or points[-1][0]-points[0][0]<60:
        return {'valid':False,'reason':'insufficient_valid_history','model':'robust_linear_baseline'}
    slopes=[(b[1]-a[1])/(b[0]-a[0]) for i,a in enumerate(points) for b in points[i+1:] if b[0]>a[0]]
    slope=statistics.median(slopes);last_t=points[-1][0]
    level=statistics.median([p-slope*(t-last_t) for t,p in points])
    residual=[abs(p-(level+slope*(t-last_t))) for t,p in points]
    dispersion=statistics.median(residual)
    prediction=max(0.0,level+slope*horizon_s)
    return {'valid':True,'model':'robust_linear_baseline','horizon_s':horizon_s,
        'predicted_w':prediction,'historical_residual_mad_w':dispersion,
        'samples':len(points),'is_calibrated_prediction_interval':False,
        'warning':'Baseline only; backtest on real data before scheduling; not measured savings'}

if __name__=='__main__':main()
