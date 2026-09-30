import unittest
from dataclasses import replace
from policy_reference import Command, Endpoint, Profile, Snapshot


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.endpoint = Endpoint()
        self.profile = Profile('approved-switchable', True, False, True)
        self.snapshot = Snapshot(1000)
        self.command = Command('cmd-1', 'CM-SIM-001', self.profile.profile_id,
                               'shed', 995, 1045, 1, True, True)

    def run_cmd(self, **changes):
        args = dict(cmd=self.command, profile=self.profile,
                    snapshot=self.snapshot, now=1000)
        args.update(changes)
        return self.endpoint.apply(**args)['status']

    def test_valid_shed(self):
        self.assertEqual(self.run_cmd(), 'ACCEPTED')
        self.assertFalse(self.endpoint.energized)

    def test_unknown_monitor_only(self):
        self.assertEqual(self.run_cmd(profile=Profile(), cmd=replace(self.command, profile_id='unknown')),
                         'UNKNOWN_LOAD_MONITOR_ONLY')
        self.assertTrue(self.endpoint.energized)

    def test_unapproved(self):
        self.assertEqual(self.run_cmd(profile=replace(self.profile, approved=False)), 'UNKNOWN_LOAD_MONITOR_ONLY')

    def test_critical_load(self):
        self.assertEqual(self.run_cmd(profile=replace(self.profile, critical=True)), 'CRITICAL_LOAD_EXCLUDED')

    def test_normal_interface_ac_not_mains_chopped(self):
        self.assertEqual(self.run_cmd(profile=replace(self.profile, allow_mains_shed=False)), 'CAPABILITY_DENIED')

    def test_expired(self):
        self.assertEqual(self.run_cmd(cmd=replace(self.command, expires_at=1000)), 'EXPIRED_OR_INVALID_WINDOW')

    def test_future_command(self):
        self.assertEqual(self.run_cmd(cmd=replace(self.command, issued_at=1001)), 'EXPIRED_OR_INVALID_WINDOW')

    def test_overlong_ttl(self):
        self.assertEqual(self.run_cmd(cmd=replace(self.command, expires_at=1200)), 'EXPIRED_OR_INVALID_WINDOW')

    def test_stale_and_future_and_invalid_samples(self):
        for snap in (Snapshot(980), Snapshot(1001), Snapshot(1000, valid=False), Snapshot(float('nan'))):
            with self.subTest(snap=snap):
                self.assertEqual(self.run_cmd(snapshot=snap), 'STALE_OR_INVALID_DATA')

    def test_local_safety_outranks_everything(self):
        self.assertEqual(self.run_cmd(snapshot=Snapshot(0, local_trip=True), online=False,
                                     cmd=replace(self.command, authenticated=False)), 'LOCAL_SAFETY_TRIP')
        self.assertFalse(self.endpoint.energized)

    def test_fault_latched_no_remote_restore(self):
        self.run_cmd(snapshot=Snapshot(1000, local_trip=True))
        self.assertEqual(self.run_cmd(cmd=replace(self.command, action='restore')), 'LOCAL_SAFETY_TRIP')

    def test_duplicate_no_reactuation(self):
        self.run_cmd()
        changed_at = self.endpoint.changed_at
        self.assertEqual(self.run_cmd(now=1100), 'DUPLICATE')
        self.assertEqual(self.endpoint.changed_at, changed_at)

    def test_duplicate_cannot_suppress_local_trip(self):
        self.run_cmd(cmd=replace(self.command, action='hold'))
        self.assertEqual(self.run_cmd(snapshot=Snapshot(1000, local_trip=True)), 'LOCAL_SAFETY_TRIP')

    def test_id_conflict(self):
        self.run_cmd()
        self.assertEqual(self.run_cmd(cmd=replace(self.command, action='restore')), 'ID_CONFLICT')

    def test_replay_sequence(self):
        self.run_cmd()
        self.assertEqual(self.run_cmd(cmd=replace(self.command, command_id='cmd-2')), 'REPLAY_SEQUENCE')

    def test_offline_holds_state(self):
        self.assertEqual(self.run_cmd(online=False), 'OFFLINE_HOLD')
        self.assertTrue(self.endpoint.energized)
        self.endpoint.energized = False
        self.assertEqual(self.run_cmd(online=False, cmd=replace(self.command, action='restore')), 'OFFLINE_HOLD')
        self.assertFalse(self.endpoint.energized)

    def test_reconnected_old_command_rejected(self):
        self.run_cmd(online=False)
        self.assertEqual(self.run_cmd(now=1100, snapshot=Snapshot(1100)), 'EXPIRED_OR_INVALID_WINDOW')

    def test_authentication_and_authorization(self):
        for field in ('authenticated', 'authorized'):
            self.assertEqual(self.run_cmd(cmd=replace(self.command, **{field: False})), 'UNAUTHORIZED')

    def test_wrong_device_and_profile(self):
        self.assertEqual(self.run_cmd(cmd=replace(self.command, device_id='other')), 'WRONG_DEVICE')
        self.assertEqual(self.run_cmd(cmd=replace(self.command, profile_id='other')), 'PROFILE_MISMATCH')

    def test_dwell(self):
        self.endpoint.changed_at = 999
        self.assertEqual(self.run_cmd(), 'MINIMUM_DWELL')

    def test_restore_after_dwell(self):
        self.endpoint.energized = False
        self.assertEqual(self.run_cmd(cmd=replace(self.command, action='restore')), 'ACCEPTED')
        self.assertTrue(self.endpoint.energized)

    def test_untrusted_clock(self):
        self.assertEqual(self.run_cmd(clock_trusted=False), 'UNTRUSTED_CLOCK')

    def test_voltage_modulation_rejected(self):
        self.assertEqual(self.run_cmd(cmd=replace(self.command, action='set_voltage')), 'UNSUPPORTED_ACTION')

    def test_local_idle(self):
        self.assertEqual(self.run_cmd(cmd=None), 'NO_COMMAND')


if __name__ == '__main__':
    unittest.main()
