delete from locks 
where board_name = '{{ board_name | sqlsafe }}' 
and user_id = '{{ user_id | sqlsafe }}'
