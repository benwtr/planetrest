drop table if exists users;
create table users (
  id         integer primary key autoincrement,
  first_name text    not null,
  last_name  text    not null,
  userid     text    not null unique
);

drop table if exists groups;
create table groups (
  id         integer primary key autoincrement,
  group_name text    not null unique
);

drop table if exists membership;
create table membership (
  user_id  integer not null,
  group_id integer not null,
  primary key (user_id, group_id) on conflict replace,
  foreign key(user_id) references users(id) on delete cascade,
  foreign key(group_id) references groups(id) on delete cascade
);

