-- get all cpu cores of a board with their cpus extensions
with board_cpu_core_extension (board_id, os_id, cpu_extensions) as (
    select bcc.board_id, bcc.os_id, array_agg(ce.name) as extensions 
    from board_cpu_cores bcc
    inner join board_cpu_core_extensions as bcce on bcc.id = bcce.board_cpu_core_id
    inner join cpu_extensions as ce on bcce.cpu_extension_id = ce.id
    group by bcc.id
) 

select 
    bcc.os_id as os_id, 
    cisa.name as isa, 
    cu.name as uarch, 
    ci.name as implementer, 
    bcce.cpu_extensions as extensions
from boards as b 
inner join board_cpu_cores as bcc on bcc.board_id = b.id
inner join cpu_uarch_implementations as cui on bcc.cpu_uarch_implementation_id = cui.id
inner join cpu_uarchs as cu on cui.cpu_uarch_id = cu.id
inner join cpu_implementers as ci on cui.cpu_implementer_id = ci.id
inner join cpu_isas as cisa on bcc.cpu_isa_id = cisa.id
inner join board_cpu_core_extension as bcce on bcce.board_id = b.id and bcce.os_id = bcc.os_id
where b.id ={{ board_id | sqlsafe }} 
