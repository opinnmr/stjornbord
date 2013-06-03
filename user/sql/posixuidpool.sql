-- These can't be created with fixtures because they depend on what
-- content type id the ou and student model's get. The StjornbordTestCase
-- populates these for the test cases

INSERT INTO user_posixuidpool  (user_type_id, next_uid)
SELECT id, 500000 FROM django_content_type WHERE app_label = "ou" and model = "organizationalunit";

INSERT INTO user_posixuidpool  (user_type_id, next_uid)
SELECT id, 1000000 FROM django_content_type WHERE app_label = "student" and model = "student";
