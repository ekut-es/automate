-- get os for board
select 
    boss.id as id,
    m.name as machine, 
    oss.name as os,
    e.name as environment, 
    d.name as distribution, 
    boss.release as release, 
    boss.description as description, 
    boss.sysroot as sysroot,
    boss.rootfs as rootfs,
    boss.multiarch as multiarch
from board_oss as boss
inner join boards as b on b.id = boss.board_id
inner join oss as oss on oss.id = boss.os_id
inner join machines as m on m.id = boss.machine_id
inner join environments as e on e.id = boss.environment_id
inner join distributions as d on d.id = boss.distribution_id
where b.id = {{ board_id | sqlsafe }} 
