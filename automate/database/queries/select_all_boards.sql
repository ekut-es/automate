select
    b.name as name,
    b.hostname as hostname,
    b.id as id,
    b.description as description,
    b.ssh_username as ssh_username,
    b.ssh_port as ssh_port
from boards as b
