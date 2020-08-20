begin;
-- drop all tables
drop table if exists board_cpu_core_extensions;
drop table if exists board_cpu_cores;

drop table if exists os_kernels;
drop table if exists board_oss;

drop table if exists oss;
drop table if exists machines;
drop table if exists environments;
drop table if exists distributions;
drop table if exists docs;

drop table if exists boards;

drop table if exists cpu_uarch_implementations;

drop table if exists cpu_isas;
drop table if exists cpu_uarchs;
drop table if exists cpu_implementers;
drop table if exists cpu_extensions;

drop table if exists power_connectors;
drop table if exists socs;

drop table if exists foundries;

drop table if exists locks;

create table foundries (
    id serial primary key,
    name varchar(255),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

create table socs (
    id serial primary key,
    name varchar(255),
    technology integer, -- nm
    foundry_id integer references foundries(id),
    check(technology > 0),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

create table power_connectors (
    id serial primary key,
    name varchar(255),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

create table boards (
    id serial primary key,
    name varchar(255),
    hostname varchar(32), 
    description varchar(255),
    soc_id integer references socs(id) not null,
    power_connector_id integer references power_connectors(id) not null,
    voltage real, -- voltage in V
    max_current real, -- max. current in A
    mac_address macaddr,
    ssh_username varchar(255),
    ssh_port integer not null,
    unique(hostname),
    check(name is not null and length(trim(name)) > 0),
    check(hostname is not null and length(trim(hostname)) > 0),
    check(description is not null and length(trim(description)) > 0),
    check(ssh_username is not null and length(trim(description)) > 0),
    check(voltage >= 0.0),
    check(max_current >= 0.0)
);

create table cpu_isas (
    id serial primary key,
    name varchar(32),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

insert into cpu_isas(name)
values
	('armv2'),
	('armv2a'),
	('armv3'),
	('armv3m'),
	('armv4'),
	('armv4t'),
	('armv5'),
	('armv5t'),
	('armv5e'),
	('armv5te'),
	('armv5tej'),
	('armv6'),
	('armv6j'),
	('armv6k'),
	('armv6z'),
	('armv6kz'),
	('armv6zk'),
	('armv6t2'),
	('armv6-m'),
	('armv6s-m'),
	('armv7'),
	('armv7-a'),
	('armv7ve'),
	('armv7-r'),
	('armv7-m'),
	('armv7e-m'),
	('armv8-a'),
	('armv8.1-a'),
	('armv8.2-a'),
	('armv8.3-a'),
	('armv8.4-a'),
	('armv8.5-a'),
	('armv8-m.base'),
	('armv8-m.main'),
	('armv8-r'),
	('iwmmxt'),
	('iwmmxt2');

create table cpu_implementers (
    id integer not null, -- Why not id serial primary key,
    name varchar(32),
    unique(id),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

insert into cpu_implementers(id, name)
values
    (x'41'::int, 'arm'),
    (x'42'::int, 'broadcom'),
    (x'43'::int, 'cavium'),
    (x'44'::int, 'dec'),
    (x'48'::int, 'hisilicon'),
    (x'49'::int, 'infinion'),
    (x'4e'::int, 'nvidia'),
    (x'50'::int, 'apm'),
    (x'51'::int, 'qualcomm'),
    (x'53'::int, 'samsung'),
    (x'56'::int, 'marvell'),
    (x'66'::int, 'faraday'),
    (x'69'::int, 'intel');

create table cpu_uarchs (
    id serial primary key,
    name varchar(32),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

insert into cpu_uarchs(name)
values
	('arm1020e'),
	('arm1020t'),
	('arm1022e'),
	('arm1026ej-s'),
	('arm10e'),
	('arm10tdmi'),
	('arm1136jf-s'),
	('arm1136j-s'),
	('arm1156t2f-s'),
	('arm1156t2-s'),
	('arm1176jzf-s'),
	('arm1176jz-s'),
	('arm2'),
	('arm250'),
	('arm3'),
	('arm6'),
	('arm60'),
	('arm600'),
	('arm610'),
	('arm620'),
	('arm7'),
	('arm70'),
	('arm700'),
	('arm700i'),
	('arm710'),
	('arm7100'),
	('arm710c'),
	('arm710t'),
	('arm720'),
	('arm720t'),
	('arm740t'),
	('arm7500'),
	('arm7500fe'),
	('arm7d'),
	('arm7di'),
	('arm7dm'),
	('arm7dmi'),
	('arm7m'),
	('arm7tdmi'),
	('arm7tdmi-s'),
	('arm8'),
	('arm810'),
	('arm9'),
	('arm920'),
	('arm920t'),
	('arm922t'),
	('arm926ej-s'),
	('arm940t'),
	('arm946e-s'),
	('arm966e-s'),
	('arm968e-s'),
	('arm9e'),
	('arm9tdmi'),
	('carmel'),
	('cortex-a12'),
	('cortex-a15'),
	('cortex-a17'),
	('cortex-a32'),
	('cortex-a35'),
	('cortex-a5'),
	('cortex-a53'),
	('cortex-a55'),
	('cortex-a57'),
	('cortex-a7'),
	('cortex-a72'),
	('cortex-a73'),
	('cortex-a75'),
	('cortex-a76'),
	('cortex-a77'),
	('cortex-a8'),
	('cortex-a9'),
	('cortex-m0'),
	('cortex-m0plus'),
	('cortex-m0plus.small-multiply'),
	('cortex-m0.small-multiply'),
	('cortex-m1'),
	('cortex-m1.small-multiply'),
	('cortex-m23'),
	('cortex-m3'),
	('cortex-m33'),
	('cortex-m4'),
	('cortex-m7'),
	('cortex-r4'),
	('cortex-r4f'),
	('cortex-r5'),
	('cortex-r52'),
	('cortex-r7'),
	('cortex-r8'),
	('denver'),
	('denver2'),
	('ep9312'),
	('exynos-m1'),
	('fa526'),
	('fa606te'),
	('fa626'),
	('fa626te'),
	('fa726te'),
	('falkor'),
	('fmp626'),
	('generic-armv7-a'),
	('iwmmxt'),
	('iwmmxt2'),
	('marvell-pj4'),
	('arm11-mpcore'),
	('arm11-mpcorenovfp'),
	('qdf24xx'),
	('saphira'),
	('strongarm'),
	('strongarm110'),
	('strongarm1100'),
	('strongarm1110'),
	('thunderx'),
	('thunderx2t99'),
	('thunderx2t99p1'),
	('thunderxt81'),
	('thunderxt83'),
	('thunderxt88'),
	('thunderxt88p1'),
	('vulcan'),
	('xgene1'),
	('xscale'),
	('neoverse-n1'),
	('neoverse-e1'),
	('brahma-b15'),
	('brahma-b32'),
	('brahma-b53'),
	('sa110'),
	('sa1100'),
	('scorpion'),
	('krait'),
	('kryo'),
	('tsv110');

create table cpu_uarch_implementations (
    id serial primary key,
    cpu_uarch_id integer references cpu_uarchs(id) not null,
    cpu_implementer_id integer references cpu_implementers(id) not null,
    cpu_part_id integer not null,
    unique(cpu_uarch_id, cpu_implementer_id, cpu_part_id)
);

insert into cpu_uarch_implementations(cpu_uarch_id, cpu_implementer_id, cpu_part_id)
values
	((select id from cpu_uarchs where name = 'arm810'), (select id from cpu_implementers where name = 'arm'), x'810'::int),
	((select id from cpu_uarchs where name = 'arm920'), (select id from cpu_implementers where name = 'arm'), x'920'::int),
	((select id from cpu_uarchs where name = 'arm922t'), (select id from cpu_implementers where name = 'arm'), x'922'::int),
	((select id from cpu_uarchs where name = 'arm926ej-s'), (select id from cpu_implementers where name = 'arm'), x'926'::int),
	((select id from cpu_uarchs where name = 'arm940t'), (select id from cpu_implementers where name = 'arm'), x'940'::int),
	((select id from cpu_uarchs where name = 'arm946e-s'), (select id from cpu_implementers where name = 'arm'), x'946'::int),
	((select id from cpu_uarchs where name = 'arm966e-s'), (select id from cpu_implementers where name = 'arm'), x'966'::int),
	((select id from cpu_uarchs where name = 'arm1020e'), (select id from cpu_implementers where name = 'arm'), x'a20'::int),
	((select id from cpu_uarchs where name = 'arm1022e'), (select id from cpu_implementers where name = 'arm'), x'a22'::int),
	((select id from cpu_uarchs where name = 'arm1026ej-s'), (select id from cpu_implementers where name = 'arm'), x'a26'::int),
	((select id from cpu_uarchs where name = 'arm11-mpcore'), (select id from cpu_implementers where name = 'arm'), x'b02'::int),
	((select id from cpu_uarchs where name = 'arm1136j-s'), (select id from cpu_implementers where name = 'arm'), x'b36'::int),
	((select id from cpu_uarchs where name = 'arm1156t2-s'), (select id from cpu_implementers where name = 'arm'), x'b56'::int),
	((select id from cpu_uarchs where name = 'arm1176jz-s'), (select id from cpu_implementers where name = 'arm'), x'b76'::int),
	((select id from cpu_uarchs where name = 'cortex-a5'), (select id from cpu_implementers where name = 'arm'), x'c05'::int),
	((select id from cpu_uarchs where name = 'cortex-a7'), (select id from cpu_implementers where name = 'arm'), x'c07'::int),
	((select id from cpu_uarchs where name = 'cortex-a8'), (select id from cpu_implementers where name = 'arm'), x'c08'::int),
	((select id from cpu_uarchs where name = 'cortex-a9'), (select id from cpu_implementers where name = 'arm'), x'c09'::int),
	((select id from cpu_uarchs where name = 'cortex-a17'), (select id from cpu_implementers where name = 'arm'), x'c0e'::int),
	((select id from cpu_uarchs where name = 'cortex-a15'), (select id from cpu_implementers where name = 'arm'), x'c0f'::int),
	((select id from cpu_uarchs where name = 'cortex-r4'), (select id from cpu_implementers where name = 'arm'), x'c14'::int),
	((select id from cpu_uarchs where name = 'cortex-r5'), (select id from cpu_implementers where name = 'arm'), x'c15'::int),
	((select id from cpu_uarchs where name = 'cortex-r7'), (select id from cpu_implementers where name = 'arm'), x'c17'::int),
	((select id from cpu_uarchs where name = 'cortex-r8'), (select id from cpu_implementers where name = 'arm'), x'c18'::int),
	((select id from cpu_uarchs where name = 'cortex-m0'), (select id from cpu_implementers where name = 'arm'), x'c20'::int),
	((select id from cpu_uarchs where name = 'cortex-m1'), (select id from cpu_implementers where name = 'arm'), x'c21'::int),
	((select id from cpu_uarchs where name = 'cortex-m3'), (select id from cpu_implementers where name = 'arm'), x'c23'::int),
	((select id from cpu_uarchs where name = 'cortex-m4'), (select id from cpu_implementers where name = 'arm'), x'c24'::int),
	((select id from cpu_uarchs where name = 'cortex-m7'), (select id from cpu_implementers where name = 'arm'), x'c27'::int),
	((select id from cpu_uarchs where name = 'cortex-m0plus'), (select id from cpu_implementers where name = 'arm'), x'c60'::int),
	((select id from cpu_uarchs where name = 'cortex-a32'), (select id from cpu_implementers where name = 'arm'), x'd01'::int),
	((select id from cpu_uarchs where name = 'cortex-a53'), (select id from cpu_implementers where name = 'arm'), x'd03'::int),
	((select id from cpu_uarchs where name = 'cortex-a35'), (select id from cpu_implementers where name = 'arm'), x'd04'::int),
	((select id from cpu_uarchs where name = 'cortex-a55'), (select id from cpu_implementers where name = 'arm'), x'd05'::int),
	((select id from cpu_uarchs where name = 'cortex-a57'), (select id from cpu_implementers where name = 'arm'), x'd07'::int),
	((select id from cpu_uarchs where name = 'cortex-a72'), (select id from cpu_implementers where name = 'arm'), x'd08'::int),
	((select id from cpu_uarchs where name = 'cortex-a73'), (select id from cpu_implementers where name = 'arm'), x'd09'::int),
	((select id from cpu_uarchs where name = 'cortex-a75'), (select id from cpu_implementers where name = 'arm'), x'd0a'::int),
	((select id from cpu_uarchs where name = 'cortex-a76'), (select id from cpu_implementers where name = 'arm'), x'd0b'::int),
	((select id from cpu_uarchs where name = 'neoverse-n1'), (select id from cpu_implementers where name = 'arm'), x'd0c'::int),
	((select id from cpu_uarchs where name = 'cortex-r52'), (select id from cpu_implementers where name = 'arm'), x'd13'::int),
	((select id from cpu_uarchs where name = 'cortex-m23'), (select id from cpu_implementers where name = 'arm'), x'd20'::int),
	((select id from cpu_uarchs where name = 'cortex-m33'), (select id from cpu_implementers where name = 'arm'), x'd21'::int),
	((select id from cpu_uarchs where name = 'neoverse-e1'), (select id from cpu_implementers where name = 'arm'), x'd4a'::int),
	((select id from cpu_uarchs where name = 'brahma-b15'), (select id from cpu_implementers where name = 'broadcom'), x'00f'::int),
	((select id from cpu_uarchs where name = 'brahma-b53'), (select id from cpu_implementers where name = 'broadcom'), x'100'::int),
	((select id from cpu_uarchs where name = 'thunderx2t99'), (select id from cpu_implementers where name = 'broadcom'), x'516'::int),
	((select id from cpu_uarchs where name = 'sa110'), (select id from cpu_implementers where name = 'dec'), x'a10'::int),
	((select id from cpu_uarchs where name = 'sa1100'), (select id from cpu_implementers where name = 'dec'), x'a11'::int),
	((select id from cpu_uarchs where name = 'thunderx'), (select id from cpu_implementers where name = 'cavium'), x'0a0'::int),
	((select id from cpu_uarchs where name = 'thunderxt88'), (select id from cpu_implementers where name = 'cavium'), x'0a1'::int),
	((select id from cpu_uarchs where name = 'thunderxt81'), (select id from cpu_implementers where name = 'cavium'), x'0a2'::int),
	((select id from cpu_uarchs where name = 'thunderxt83'), (select id from cpu_implementers where name = 'cavium'), x'0a3'::int),
	((select id from cpu_uarchs where name = 'xgene1'), (select id from cpu_implementers where name = 'apm'), x'000'::int),
	((select id from cpu_uarchs where name = 'scorpion'), (select id from cpu_implementers where name = 'qualcomm'), x'00f'::int),
	((select id from cpu_uarchs where name = 'scorpion'), (select id from cpu_implementers where name = 'qualcomm'), x'02d'::int),
	((select id from cpu_uarchs where name = 'krait'), (select id from cpu_implementers where name = 'qualcomm'), x'04d'::int),
	((select id from cpu_uarchs where name = 'krait'), (select id from cpu_implementers where name = 'qualcomm'), x'06f'::int),
	((select id from cpu_uarchs where name = 'kryo'), (select id from cpu_implementers where name = 'qualcomm'), x'201'::int),
	((select id from cpu_uarchs where name = 'kryo'), (select id from cpu_implementers where name = 'qualcomm'), x'205'::int),
	((select id from cpu_uarchs where name = 'kryo'), (select id from cpu_implementers where name = 'qualcomm'), x'211'::int),
	((select id from cpu_uarchs where name = 'falkor'), (select id from cpu_implementers where name = 'qualcomm'), x'c00'::int),
	((select id from cpu_uarchs where name = 'saphira'), (select id from cpu_implementers where name = 'qualcomm'), x'c01'::int),
	((select id from cpu_uarchs where name = 'exynos-m1'), (select id from cpu_implementers where name = 'samsung'), x'001'::int),
	((select id from cpu_uarchs where name = 'denver'), (select id from cpu_implementers where name = 'nvidia'), x'000'::int),
	((select id from cpu_uarchs where name = 'denver2'), (select id from cpu_implementers where name = 'nvidia'), x'003'::int),
	((select id from cpu_uarchs where name = 'carmel'), (select id from cpu_implementers where name = 'nvidia'), x'004'::int),
	((select id from cpu_uarchs where name = 'tsv110'), (select id from cpu_implementers where name = 'hisilicon'), x'D01'::int);

create table cpu_extensions (
    id serial primary key,
    name varchar(32),
    unique(name),
    check(name is not null and length(trim(name)) > 0)
);

create table board_cpu_cores (
    id serial primary key,
    board_id integer references boards(id) not null,
    cpu_isa_id integer references cpu_isas(id) not null,
    cpu_uarch_implementation_id integer references cpu_uarch_implementations(id) not null,
    os_id integer not null, -- id which is displayed after "processor" when executing: cat /proc/cpuinfo
    unique(board_id, os_id)
);

create table board_cpu_core_extensions (
    board_cpu_core_id integer references board_cpu_cores(id) not null,
    cpu_extension_id integer references cpu_extensions(id),
    unique(board_cpu_core_id, cpu_extension_id)
);

create table oss (
    id serial primary key,
    name varchar(32),
    unique(name)
);

create table machines (
    id serial primary key,
    name varchar(32),
    unique(name)
);

create table environments (
    id serial primary key,
    name varchar(32),
    unique(name)
);

create table distributions (
    id serial primary key,
    name varchar(32),
    unique(name)
);

create table board_oss (
    id serial primary key,
    board_id integer references boards(id) not null,
    os_id integer references oss(id) not null,
    machine_id integer references machines(id) not null,
    environment_id integer references environments(id) not null,
    distribution_id integer references distributions(id) not null,
    release varchar(32),
    description varchar(255),
    sysroot varchar(255),
    rootfs varchar(255),
    multiarch boolean,
    unique(board_id, os_id, machine_id, environment_id, distribution_id, release, description)
);

create table os_kernels (
    id serial primary key,
    board_os_id integer references board_oss(id) not null,
    name varchar(32),
    description varchar(255),
    version varchar(255),
    command_line text,
    kernel_config varchar(255),
    kernel_source varchar(255),
    kernel_srcdir varchar(255),
    image_build_path varchar(255),
    image_deploy_path varchar(255),
    uboot_loadaddr varchar(255),
    uboot_image_name varchar(255),
    uboot_dtb_image varchar(255),
    is_default boolean default false
);

create unique index only_one_default_kernel_per_board_os on os_kernels(board_os_id) where is_default;

create table docs (
    id serial primary key,
    board_id integer references boards(id) ,
    title varchar(255),
    location varchar(1024),
    unique(board_id, title, location)
);

create table locks (
    board_name varchar(255) not null,
    user_id varchar(255) not null,
    lease timestamp with time zone not null,
    unique(board_name)
);