drop table if exists pages;
drop table if exists tags;
drop table if exists pages_tags_assoc;

create table pages (
    id integer primary key autoincrement,
    name text not null,
    body text
);

create table tags (
    id integer primary key autoincrement,
    name text not null
);

create table pages_tags_assoc (
    pageid integer,
    tagid integer,
    FOREIGN KEY(pageid) REFERENCES pages(id),
    FOREIGN KEY(tagid) REFERENCES tags(id)
);
