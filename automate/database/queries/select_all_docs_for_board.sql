select 
    d.title as title,
    d.location as location
from docs as d
inner join boards as b on b.id = d.board_id
where b.id = {{ board_id | sqlsafe }} 
