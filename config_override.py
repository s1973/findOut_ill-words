"""
Override configurations.
"""

configs = {
    'db': {
        'host': "10.0.0.232",
        "user": "root",
        "password": "17e0ab4a0bdc3871",
        "db": 'hb_mpm'
    },
    'db2':{
        'host': "10.0.0.232",
        "user": "root",
        "password": "17e0ab4a0bdc3871"
    }
}

'''
CREATE TABLE `illegal_result` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `keys` mediumtext NOT NULL,
  `title` text NOT NULL,
  `postid` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `class_name` varchar(255) NOT NULL,
  `t_table` char(50) NOT NULL,
  `created_at` int(11) NOT NULL,
  `sitename` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `en_project` varchar(255) NOT NULL,
  `siteid` int(11) NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8

CREATE TABLE `illegal_words` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `word` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8
'''