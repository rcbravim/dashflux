--drop table if exists user;
--drop table if exists board_analytic;
--drop table if exists board_category;
--drop table if exists board_beneficiary;
--drop table if exists board_client;
--drop table if exists board_financial;
--drop table if exists board_subcategory;
--drop table if exists board_release;
--drop table if exists board_beneficiary;
--drop table if exists board_beneficiarycategory;
--drop table if exists board_client;
--drop table if exists board_country;
--drop table if exists board_state;
--drop table if exists board_userlog;

CREATE TABLE IF NOT EXISTS user (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	use_login VARCHAR(250) NOT NULL,
	use_password VARCHAR(128) NOT NULL,
	use_status TINYINT(1) NOT NULL,
	use_date_created DATETIME(6) NOT NULL,
	use_date_updated DATETIME(6) NOT NULL,
	use_date_deleted DATETIME(6) NULL DEFAULT NULL,
	use_is_valid TINYINT(1) NOT NULL,
	use_is_manager TINYINT(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS board_analytic (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  ana_cycle date NOT NULL,
  ana_json longtext NOT NULL,
  ana_status tinyint(1) NOT NULL,
  ana_date_created datetime(6) NOT NULL,
  ana_date_updated datetime(6) NOT NULL,
  ana_date_deleted datetime(6) DEFAULT NULL,
  user_id INTEGER NOT NULL,
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id) ON UPDATE RESTRICT ON DELETE RESTRICT
 );


CREATE TABLE IF NOT EXISTS board_category (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	cat_name VARCHAR(250) NOT NULL,
	cat_slug VARCHAR(250) UNIQUE NOT NULL,
	cat_status TINYINT(1) NOT NULL,
	cat_date_created DATETIME(6) NOT NULL,
	cat_date_updated DATETIME(6) NOT NULL,
	cat_date_deleted DATETIME(6) NULL DEFAULT NULL,
	user_id INTEGER NOT NULL,
	cat_type SMALLINT(6) NOT NULL,
	CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS board_subcategory (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	sub_name VARCHAR(250) NOT NULL,
	sub_slug VARCHAR(250) UNIQUE NOT NULL,
	sub_status TINYINT(1) NOT NULL,
	sub_date_created DATETIME(6) NOT NULL,
	sub_date_updated DATETIME(6) NOT NULL,
	sub_date_deleted DATETIME(6) NULL DEFAULT NULL,
	category_id BIGINT(20) NOT NULL,
	CONSTRAINT fk_category_id FOREIGN KEY (category_id) REFERENCES board_category(id) ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS board_financial (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  fin_slug varchar(250) UNIQUE NOT NULL,
  fin_cost_center varchar(250) DEFAULT NULL,
  fin_description varchar(250) DEFAULT NULL,
  fin_bank_name varchar(250) DEFAULT NULL,
  fin_bank_branch varchar(20) DEFAULT NULL,
  fin_bank_account varchar(20) DEFAULT NULL,
  fin_type smallint(6) NOT NULL,
  fin_status tinyint(1) NOT NULL,
  fin_date_created datetime(6) NOT NULL,
  fin_date_updated datetime(6) NOT NULL,
  fin_date_deleted datetime(6) DEFAULT NULL,
  user_id INTEGER DEFAULT NULL,
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id)
);


 CREATE TABLE IF NOT EXISTS board_release (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  rel_slug varchar(250) UNIQUE NOT NULL,
  rel_gen_status smallint(6) NOT NULL,
  rel_entry_date date NOT NULL,
  rel_amount decimal(15,3) NOT NULL,
  rel_monthly_balance decimal(15,3) NOT NULL,
  rel_overall_balance decimal(15,3) NOT NULL,
  rel_description varchar(250) DEFAULT NULL,
  rel_sqn int(11) NOT NULL,
  rel_status tinyint(1) NOT NULL,
  rel_date_created datetime(6) NOT NULL,
  rel_date_updated datetime(6) NOT NULL,
  rel_date_deleted datetime(6) DEFAULT NULL,
  beneficiary_id bigint(20) DEFAULT NULL,
  client_id bigint(20) DEFAULT NULL,
  financial_account_id bigint(20) DEFAULT NULL,
  financial_cost_center_id bigint(20) DEFAULT NULL,
  subcategory_id bigint(20) DEFAULT NULL,
  user_id INTEGER NOT NULL,
  CONSTRAINT fk_beneficiary_id FOREIGN KEY (beneficiary_id) REFERENCES board_beneficiary(id),
  CONSTRAINT fk_client_id FOREIGN KEY (client_id) REFERENCES board_client(id),
  CONSTRAINT fk_financial_account_id FOREIGN KEY (financial_account_id) REFERENCES board_financial(id),
  CONSTRAINT fk_financial_cost_center_id FOREIGN KEY (financial_cost_center_id) REFERENCES board_financial(id),
  CONSTRAINT fk_subcategory_id FOREIGN KEY (subcategory_id) REFERENCES board_subcategory(id),
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS board_beneficiary (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  ben_name varchar(250) NOT NULL,
  ben_status tinyint(1) NOT NULL,
  ben_date_created datetime(6) NOT NULL,
  ben_date_updated datetime(6) NOT NULL,
  ben_date_deleted datetime(6) DEFAULT NULL,
  beneficiary_category_id bigint(20) NOT NULL,
  user_id bigint(20) NOT NULL,
  ben_slug varchar(250) UNIQUE NOT NULL,
  CONSTRAINT fk_beneficiary_category_id FOREIGN KEY (beneficiary_category_id) REFERENCES board_beneficiarycategory(id),
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE IF NOT EXISTS board_beneficiarycategory (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  cat_description varchar(250) NOT NULL,
  cat_status tinyint(1) NOT NULL,
  cat_date_created datetime(6) NOT NULL,
  cat_date_updated datetime(6) NOT NULL,
  cat_date_deleted datetime(6) DEFAULT NULL,
  user_id bigint(20) DEFAULT NULL,
  cat_slug varchar(250) UNIQUE NOT NULL,
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE IF NOT EXISTS board_client (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  cli_name varchar(250) NOT NULL,
  cli_city varchar(250) NOT NULL,
  cli_email varchar(250) DEFAULT NULL,
  cli_phone varchar(20) DEFAULT NULL,
  cli_responsible varchar(250) DEFAULT NULL,
  cli_status tinyint(1) NOT NULL,
  cli_date_created datetime(6) NOT NULL,
  cli_date_updated datetime(6) NOT NULL,
  cli_date_deleted datetime(6) DEFAULT NULL,
  country_id bigint(20) DEFAULT NULL,
  state_id bigint(20) DEFAULT NULL,
  user_id bigint(20) NOT NULL,
  cli_slug varchar(250) UNIQUE NOT NULL,
  CONSTRAINT fk_country_id FOREIGN KEY (country_id) REFERENCES board_country(id),
  CONSTRAINT fk_state_id FOREIGN KEY (state_id) REFERENCES board_state(id),
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE IF NOT EXISTS board_country (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  cou_name varchar(250) UNIQUE NOT NULL,
  cou_iso char(2) UNIQUE NOT NULL,
  cou_status tinyint(1) NOT NULL,
  cou_date_created datetime(6) NOT NULL,
  cou_date_updated datetime(6) NOT NULL,
  cou_date_deleted datetime(6) DEFAULT NULL,
  cou_phone_digits varchar(128) NOT NULL,
  cou_country_code varchar(4) NOT NULL,
  cou_image varchar(250) DEFAULT NULL
);


CREATE TABLE IF NOT EXISTS board_state (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  sta_name varchar(250) NOT NULL,
  sta_status tinyint(1) NOT NULL,
  sta_date_created datetime(6) NOT NULL,
  sta_date_updated datetime(6) NOT NULL,
  sta_date_deleted datetime(6) DEFAULT NULL,
  country_id bigint(20) NOT NULL,
  CONSTRAINT fk_country_id FOREIGN KEY (country_id) REFERENCES board_country(id)
);


CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  log_user_agent varchar(250) NOT NULL,
  log_ip_address varchar(250) NOT NULL,
  log_ip_type varchar(4) DEFAULT NULL,
  log_ip_country varchar(250) DEFAULT NULL,
  log_ip_country_flag varchar(64) DEFAULT NULL,
  log_ip_region varchar(250) DEFAULT NULL,
  log_ip_city varchar(250) DEFAULT NULL,
  log_ip_latitude decimal(12,9) DEFAULT NULL,
  log_ip_longitude decimal(12,9) DEFAULT NULL,
  log_location varchar(250) DEFAULT NULL,
  log_method varchar(16) DEFAULT NULL,
  log_risk_level smallint(6) NOT NULL,
  log_risk_comment varchar(250) DEFAULT NULL,
  log_date_created datetime(6) NOT NULL,
  user_id bigint(20) DEFAULT NULL,
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user(id)
);