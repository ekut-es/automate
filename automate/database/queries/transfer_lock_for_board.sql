update locks
set user_id = '{{ user_id | sqlsafe }}',
    lease = now() + {{ lease_duration | sqlsafe }} * interval '1 second'
where board_name = '{{board_name | sqlsafe }}'
