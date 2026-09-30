"""Executable specification ONLY. No GPIO/network/crypto/real hardware integration."""
from dataclasses import dataclass, field
from typing import Optional
import hashlib
import json
import math


@dataclass(frozen=True)
class Profile:
    profile_id: str = 'unknown'
    approved: bool = False
    critical: bool = False
    allow_mains_shed: bool = False
    min_on_s: float = 300
    min_off_s: float = 300


@dataclass(frozen=True)
class Snapshot:
    sampled_at: float
    local_trip: bool = False
    valid: bool = True


@dataclass(frozen=True)
class Command:
    command_id: str
    device_id: str
    profile_id: str
    action: str
    issued_at: float
    expires_at: float
    sequence: int
    authenticated: bool = False  # TEST STUB: production must verify signatures/mTLS/roles
    authorized: bool = False     # TEST STUB: role/tenant/device policy check


@dataclass
class Endpoint:
    device_id: str = 'CM-SIM-001'
    energized: bool = True
    changed_at: float = 0
    fault_latched: bool = False
    last_sequence: int = -1
    ledger: dict = field(default_factory=dict)
    max_age_s: float = 10
    max_command_ttl_s: float = 60

    def apply(self, cmd: Optional[Command], profile: Profile, snapshot: Snapshot,
              now: float, online: bool = True, clock_trusted: bool = True):
        """Return a simulated decision; never actuate a real relay.

        Local protection wins even over a duplicate request. In real firmware the
        protection path must operate independently of this scheduler/network path.
        """
        def result(status):
            return {'status': status, 'energized': self.energized,
                    'fault_latched': self.fault_latched}
        if snapshot.local_trip or self.fault_latched:
            self.fault_latched = True
            if self.energized:
                self.energized = False
                self.changed_at = now
            return result('LOCAL_SAFETY_TRIP')
        if cmd is None:
            return result('OFFLINE_HOLD' if not online else 'NO_COMMAND')
        if not online:
            return result('OFFLINE_HOLD')
        if not cmd.authenticated or not cmd.authorized:
            return result('UNAUTHORIZED')
        if cmd.device_id != self.device_id:
            return result('WRONG_DEVICE')
        payload = json.dumps(cmd.__dict__, sort_keys=True, allow_nan=False) if all(
            math.isfinite(x) for x in (cmd.issued_at, cmd.expires_at)) else None
        if payload is None:
            return result('INVALID_TIME')
        digest = hashlib.sha256(payload.encode()).hexdigest()
        previous = self.ledger.get(cmd.command_id)
        if previous:
            return result('DUPLICATE' if previous == digest else 'ID_CONFLICT')
        if not clock_trusted or not math.isfinite(now):
            return result('UNTRUSTED_CLOCK')
        if cmd.issued_at > now or cmd.expires_at <= now or not (
                0 < cmd.expires_at - cmd.issued_at <= self.max_command_ttl_s):
            return result('EXPIRED_OR_INVALID_WINDOW')
        if cmd.sequence <= self.last_sequence:
            return result('REPLAY_SEQUENCE')
        if not snapshot.valid or not math.isfinite(snapshot.sampled_at) or not (
                0 <= now - snapshot.sampled_at <= self.max_age_s):
            return result('STALE_OR_INVALID_DATA')
        if cmd.action not in ('hold', 'shed', 'restore'):
            return result('UNSUPPORTED_ACTION')
        if cmd.profile_id != profile.profile_id:
            return result('PROFILE_MISMATCH')
        if cmd.action != 'hold':
            if not profile.approved or profile.profile_id == 'unknown':
                return result('UNKNOWN_LOAD_MONITOR_ONLY')
            if profile.critical:
                return result('CRITICAL_LOAD_EXCLUDED')
            if not profile.allow_mains_shed:
                return result('CAPABILITY_DENIED')
            target = cmd.action == 'restore'
            dwell = profile.min_on_s if self.energized else profile.min_off_s
            if not math.isfinite(dwell) or dwell < 0:
                return result('INVALID_PROFILE')
            if target != self.energized and now - self.changed_at < dwell:
                return result('MINIMUM_DWELL')
            if target != self.energized:
                self.energized = target
                self.changed_at = now
        # Only accepted commands consume sequence and enter the replay ledger.
        self.last_sequence = cmd.sequence
        self.ledger[cmd.command_id] = digest
        return result('ACCEPTED')
