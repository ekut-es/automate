update locks
set lease = now() + {{ lease_duration | sqlsafe }} * interval '1 second'
where board_name = '{{board_name | sqlsafe }}'
