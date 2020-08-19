insert into locks(
    board_name,
    user_id,
    lease
) values (
    '{{ board_name | sqlsafe }}',
    '{{ user_id | sqlsafe }}',
    now() + {{ lease_duration | sqlsafe }} * interval '1 second'
);
