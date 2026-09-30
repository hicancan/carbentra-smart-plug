"""Boundary-aware reference accounting; caller supplies a traceable applicable factor.
No real campus figures or official emission factor values are embedded here.
"""
import math
from dataclasses import dataclass
@dataclass(frozen=True)
class Factor:
    kg_co2e_per_kwh: float
    geography: str
    year: int
    source_url: str
    method: str = 'location_based'
    def validate(self):
        if not math.isfinite(self.kg_co2e_per_kwh) or self.kg_co2e_per_kwh < 0: raise ValueError('invalid factor')
        if not self.geography or not self.source_url.startswith('https://') or not 1900<=self.year<=2200: raise ValueError('factor provenance missing')
        if self.method!='location_based': raise ValueError('this reference supports location-based method only')

def reject_overlapping_meters(selected, parent_by_id):
    """Selecting a total meter and its submeter together would double-count energy."""
    if len(selected)!=len(set(selected)): raise ValueError('duplicate meter')
    chosen=set(selected)
    for meter in chosen:
        chain=set();current=meter
        while current in parent_by_id and parent_by_id[current] is not None:
            current=parent_by_id[current]
            if current in chain: raise ValueError('meter topology cycle')
            chain.add(current)
            if current in chosen: raise ValueError('parent/submeter overlap')

def purchased_electricity_emissions(kwh, factor, has_missing_intervals=False):
    factor.validate()
    if not math.isfinite(kwh) or kwh<0: raise ValueError('supply positive purchased kWh; no implicit export credit')
    return {'known_kwh':kwh,'known_kg_co2e':kwh*factor.kg_co2e_per_kwh,
        'coverage':'partial' if has_missing_intervals else 'declared_complete',
        'factor':factor.__dict__,'is_verified_reduction':False,
        'note':'Reduction requires a comparable baseline; shifting time alone does not change this fixed-factor result'}
