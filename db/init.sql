CREATE DATABASE img_processing;
CREATE ROLE img_processing_user WITH LOGIN PASSWORD 'SlOShNy_Password1';
GRANT ALL PRIVILEGES ON DATABASE img_processing TO img_processing_user;
\c img_processing
GRANT ALL ON SCHEMA public TO img_processing_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO img_processing_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO img_processing_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO img_processing_user;

CREATE DATABASE file_storage;
CREATE ROLE file_storage_user WITH LOGIN PASSWORD 'SlOShNy_Password1';
GRANT ALL PRIVILEGES ON DATABASE file_storage TO file_storage_user;
\c file_storage
GRANT ALL ON SCHEMA public TO file_storage_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO file_storage_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO file_storage_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO file_storage_user;
