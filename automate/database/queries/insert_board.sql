begin;
    -- insert foundry
    {% if foundry_name is defined -%}
    insert into foundries(name) values('{{ foundry_name | sqlsafe }}') on conflict do nothing;
    {% endif %}

    -- insert SoC
    insert into socs(
        name
        {% if technology is defined -%}
        , technology
        {%- endif %}
        {% if foundry_name is defined -%}
        , foundry_id
        {%- endif %}
    ) values (
        '{{ soc_name | sqlsafe }}'
        {% if technology is defined -%}
        , {{ technology | sqlsafe }} 
        {%- endif %}
        {% if foundry_name is defined -%}
        , (select id from foundries where name = '{{ foundry_name | sqlsafe }}')
        {%- endif %}
    )
    on conflict do nothing;

    -- insert power_connector
    insert into power_connectors(name) values ('{{ power_connector_name | sqlsafe }}') on conflict do nothing;

    -- insert into boards
    insert into boards(
        name,
        hostname,
        description,
        soc_id,
        power_connector_id,
        ssh_username,
        ssh_port
        {% if voltage is defined -%}
        , voltage
        {%- endif %}
        {% if max_current is defined -%}
        , max_current
        {%- endif %}
    ) values (
        '{{ board.name | sqlsafe }}',
        '{{ hostname | sqlsafe }}',
        '{{ board.description | sqlsafe }}',
        (select id from socs where name = '{{ soc_name | sqlsafe }}'),
        (select id from power_connectors where name = '{{ power_connector_name | sqlsafe }}'),
        '{{ board.connections[0].username | sqlsafe }}',
        '{{ board.connections[0].port | sqlsafe }}'
        {% if voltage is defined -%}
        , {{ voltage | sqlsafe }}
        {%- endif %}
        {% if max_current is defined -%}
        , {{ max_current | sqlsafe }}
        {%- endif %}
    );

    -- insert into cpu_isas
    insert into cpu_isas(name)
    values
    ('{{ cpu_isas[0] | sqlsafe }}')
    {% for cpu_isa in cpu_isas[1:] -%}
    , ('{{ cpu_isa | sqlsafe }}')
    {%- endfor %}
    on conflict do nothing;

    -- inert into cpu_uarch_implementations
    insert into cpu_uarch_implementations(cpu_uarch_id, cpu_implementer_id, cpu_part_id)
    values (
        (select id from cpu_uarchs where name = '{{ board.cores[0].uarch.value | sqlsafe }}'),
        (select id from cpu_implementers where name = '{{ board.cores[0].vendor.value | sqlsafe }}'),
		{{ cpu_part_ids[board.cores[0].id] | sqlsafe }}
    )
    {%- for cpu_core in board.cores[1:] -%}
    , (
        (select id from cpu_uarchs where name = '{{ cpu_core.uarch.value | sqlsafe }}'),
        (select id from cpu_implementers where name = '{{ cpu_core.vendor.value | sqlsafe }}'),
		{{ cpu_part_ids[cpu_core.id] | sqlsafe }}
    )
    {%- endfor -%}
    on conflict do nothing;

    -- insert into board_cpu_cores
    insert into board_cpu_cores(board_id, cpu_isa_id, cpu_uarch_implementation_id, os_id)
    values (
        (select id from boards where hostname = '{{ hostname | sqlsafe }}'),
        (select id from cpu_isas where name = '{{ board.cores[0].isa.value | sqlsafe }}'),
        (select cui.id from cpu_uarch_implementations as cui
         inner join cpu_uarchs as cu on cu.id = cui.cpu_uarch_id
         inner join cpu_implementers as ci on ci.id = cui.cpu_implementer_id
         where cu.name = '{{ board.cores[0].uarch.value | sqlsafe }}' and ci.name = '{{ board.cores[0].vendor.value | sqlsafe }}'),
        {{ board.cores[0].id | sqlsafe }}
    )
    {%- for cpu_core in board.cores[1:] -%}
    , (
        (select id from boards where hostname = '{{ hostname | sqlsafe }}'),
        (select id from cpu_isas where name = '{{ cpu_core.isa.value | sqlsafe }}'),
        (select cui.id from cpu_uarch_implementations as cui
         inner join cpu_uarchs as cu on cu.id = cui.cpu_uarch_id
         inner join cpu_implementers as ci on ci.id = cui.cpu_implementer_id
         where cu.name = '{{ cpu_core.uarch.value | sqlsafe }}' and ci.name = '{{ cpu_core.vendor.value | sqlsafe }}'),
        {{ cpu_core.id | sqlsafe }}
    )
    {%- endfor -%}
    ;

    -- insert into board_cpu_core_extensions
    insert into board_cpu_core_extensions(board_cpu_core_id, cpu_extension_id) 
    values 
    {%- set ns = namespace(place_comma = False) -%}
    {%- for cpu_core in board.cores -%}
        {%- for extension in cpu_core.extensions -%}
            {%- if not ns.place_comma -%}
                {%- set ns.place_comma = True -%}
            {%- else -%}
                ,
            {%- endif -%}
        (
            (select bcc.id 
                from board_cpu_cores as bcc
                inner join boards as b on b.id = bcc.board_id
                where b.hostname = '{{ hostname | sqlsafe }}' and bcc.os_id = '{{ cpu_core.id | sqlsafe }}'
            ),
            (select id from cpu_extensions where name = '{{ extension.value | sqlsafe }}')
        )
        {%- endfor -%}
    {%- endfor -%}
    ;

    -- insert into oss
    insert into oss(name) values('{{ board.os.triple.os.value | sqlsafe }}') on conflict do nothing;

    -- insert into environments
    insert into environments(name) values('{{ board.os.triple.environment.value | sqlsafe }}') on conflict do nothing;
    
    -- insert into machines 
    insert into machines(name) values('{{ board.os.triple.machine.value | sqlsafe }}') on conflict do nothing;

    -- insert into distributions
    insert into distributions(name) values('{{ board.os.distribution | sqlsafe }}') on conflict do nothing;

    -- insert into board_oss
    insert into board_oss(
        board_id, 
        os_id, 
        machine_id, 
        environment_id, 
        distribution_id
        {%- if board.os.release is defined -%}
        , release
        {%- endif -%}
        {%- if board.os.description is defined -%}
        , description 
        {%- endif -%}
        {%- if board.os.sysroot is defined -%}
        , sysroot 
        {%- endif -%}
        {%- if board.os.rootfs is defined -%}
        , rootfs
        {%- endif -%}
        {%- if board.os.multiarch is defined -%}
        , multiarch
        {%- endif -%}
    )
    values (
        (select id from boards where hostname = '{{ hostname | sqlsafe }}'),
        (select id from oss where name = '{{ board.os.triple.os.value | sqlsafe }}'),
        (select id from machines where name = '{{ board.os.triple.machine.value | sqlsafe }}'),
        (select id from environments where name = '{{ board.os.triple.environment.value | sqlsafe }}'),
        (select id from distributions where name = '{{ board.os.distribution | sqlsafe }}')
        {%- if board.os.release is defined %}
        , '{{ board.os.release | sqlsafe }}' 
        {%- endif -%}
        {%- if board.os.description is defined %}
        , '{{ board.os.description | sqlsafe }}'
        {%- endif -%}
        {%- if board.os.sysroot is defined %}
        , '{{ board.os.sysroot | sqlsafe }}' 
        {%- endif -%}
        {%- if board.os.rootfs is defined %}
        , '{{ board.os.rootfs | sqlsafe }}'
        {%- endif -%}
        {%- if board.os.multiarch is defined %}
        , {{ board.os.multiarch | sqlsafe }}
        {%- endif -%}
    );

    -- insert into os_kernels
    {% for kernel in board.os.kernels -%}
    insert into os_kernels(
        board_os_id
        {% if kernel.description is defined -%}
        , description
        {%- endif %}
        {% if kernel.version is defined -%}
        , version
        {%- endif %}
        {% if kernel.commandline is defined -%}
        , command_line
        {%- endif %}
        {% if kernel.kernel_config is defined -%}
        , kernel_config 
        {%- endif %}
        {% if kernel.kernel_source is defined -%}
        , kernel_source
        {%- endif %}
        {% if kernel.kernel_srcdir is defined -%}
        , kernel_srcdir
        {%- endif %}
        {% if kernel.image.build_path is defined -%}
        , image_build_path
        {%- endif %}
        {% if kernel.image.deploy_path is defined -%}
        , image_deploy_path
        {%- endif %}
        {% if kernel.uboot.loadaddr is defined -%}
        , uboot_loadaddr 
        {%- endif %}
        {% if kernel.uboot.image_name is defined -%}
        , uboot_image_name 
        {%- endif %}
        {% if kernel.uboot.dtb_image is defined -%}
        , uboot_dtb_image 
        {%- endif %}
        {% if kernel.default is defined -%}
        , is_default
        {%- endif %}
    ) values (
        (
            select boss.id 
            from board_oss as boss
            inner join boards as b on b.id = boss.board_id
            inner join oss as oss on oss.id = boss.os_id
            inner join machines as m on m.id = boss.machine_id
            inner join environments as e on e.id = boss.environment_id
            inner join distributions as d on d.id = boss.distribution_id
            where b.hostname = '{{ hostname | sqlsafe }}'
        )
        {%- if kernel.description is defined %}
        , '{{ kernel.description | sqlsafe }}' 
        {%- endif %}
        {% if kernel.version is defined -%}
        , '{{ kernel.version | sqlsafe }}'
        {%- endif %}
        {% if kernel.commandline is defined -%}
        , '{{ kernel.commandline | sqlsafe }}'
        {%- endif %}
        {% if kernel.kernel_config is defined -%}
        , '{{ kernel.kernel_config | sqlsafe }}' 
        {%- endif %}
        {% if kernel.kernel_source is defined -%}
        , '{{ kernel.kernel_source | sqlsafe }}' 
        {%- endif %}
        {% if kernel.kernel_srcdir is defined -%}
        , '{{ kernel.kernel_srcdir | sqlsafe }}'
        {%- endif %}
        {% if kernel.image.build_path is defined -%}
        , '{{ kernel.image.build_path | sqlsafe }}'
        {%- endif %}
        {% if kernel.image.deploy_path is defined -%}
        , '{{ kernel.image.deploy_path | sqlsafe }}'
        {%- endif %}
        {% if kernel.uboot.loadaddr is defined -%}
        , '{{ kernel.uboot.loadaddr | sqlsafe }}'
        {%- endif %}
        {% if kernel.uboot.image_name is defined -%}
        , '{{ kernel.uboot.image_name | sqlsafe }}'
        {%- endif %}
        {% if kernel.uboot.dtb_image is defined -%}
        , '{{ kernel.uboot.dtb_image | sqlsafe }}' 
        {%- endif %}
        {% if kernel.default is defined -%}
        , {{ kernel.default | sqlsafe }}
        {%- endif %}
    );
    {%- endfor %}

    -- insert into docs
    {%- if board.doc is defined and board.doc|length > 0 -%}
    insert into docs(board_id, title, location) 
    values
    (
        (select id from boards where hostname = '{{ hostname | sqlsafe }}'),
        ('{{ board.doc[0].title | sqlsafe }}'),
        ('{{ board.doc[0].loc | sqlsafe }}')
    )
    {%- for doc in board.doc[1:] -%}
    ,( -- TODO docs[0] needs special case without comma
        (select id from boards where hostname = '{{ hostname | sqlsafe }}'),
        ('{{ doc.title | sqlsafe }}'),
        ('{{ doc.loc | sqlsafe }}')
    )
    {%- endfor -%}
    {%- endif -%}
    ;
commit;
