select board_name, user_id, lease, now() as current_timestamp from locks
where board_name = '{{ board_name | sqlsafe }}'
