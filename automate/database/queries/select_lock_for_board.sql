select * from locks
where locks.board_name = '{{ board_name | sqlsafe }}'
