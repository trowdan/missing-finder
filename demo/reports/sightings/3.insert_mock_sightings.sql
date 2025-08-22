/* Mock Sightings Data Insert Script
   Inserts 10 sample sightings for testing and demonstration purposes
   Some sightings will match existing missing persons, some will not
   Data follows the schema defined in 2.create_sightings_table.sql */

INSERT INTO `homeward.sightings` (
  id, sighting_number, sighted_date, sighted_time, sighted_address, sighted_city, sighted_country,
  sighted_postal_code, sighted_latitude, sighted_longitude, sighted_geo,
  apparent_gender, apparent_age_range, height_estimate, weight_estimate, hair_color, eye_color,
  clothing_description, distinguishing_features, description, circumstances, confidence_level,
  photo_url, video_url, source_type, witness_name, witness_phone, witness_email,
  video_analytics_result_id, status, priority, verified, created_date, updated_date,
  created_by, notes, ml_summary
) VALUES
  -- Sighting 1: Potentially matches Emma Johnson (MP001) in San Francisco area
  ('SIG001', 'SIGHT-2024-001', '2024-08-16', '16:45:00', '789 Market Street', 'San Francisco', 'USA',
   '94103', 37.7849, -122.4094, ST_GEOGPOINT(-122.4094, 37.7849),
   'Female', '25-30', 165.0, 60.0, 'Brown', 'Blue',
   'Blue jeans, white top, carrying a backpack', 'Small scar on left cheek, appeared distressed',
   'Saw woman matching description walking quickly past coffee shop, looked anxious and kept checking phone',
   'Witness was having coffee when woman passed by storefront window', 'Medium',
   'https://example.com/sightings/sig001_photo.jpg', NULL, 'Witness', 'Robert Kim', '4155559876', 'robert.kim@email.com',
   NULL, 'Under_Review', 'High', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'witness_report', 'Witness seemed credible, provided detailed description',
   'Female sighting aged 25-30 years with brown hair and blue eyes, approximately 165cm tall and 60kg, spotted on August 16, 2024 at 4:45 PM on Market Street in San Francisco. The individual was wearing blue jeans and white top while carrying a backpack, with a distinctive small scar visible on left cheek and appeared distressed. Witness Robert Kim observed the woman walking quickly past a coffee shop, looking anxious and frequently checking her phone. The sighting occurred in the Financial District area with medium confidence level, potentially matching a missing person case. This high-priority sighting is currently under review by law enforcement, reported through witness testimony with the observer noting credible details and behavioral indicators of distress.'),


  -- Sighting 2: Potentially matches David Chen (MP002) in Los Angeles area  
  ('SIG002', 'SIGHT-2024-002', '2024-08-11', '11:30:00', '123 Corporate Plaza', 'Los Angeles', 'USA',
   '90213', 34.0622, -118.2537, ST_GEOGPOINT(-118.2537, 34.0622),
   'Male', '35-40', 178.0, 75.0, 'Black', 'Brown',
   'Dark business suit, appeared professional', 'Visible tattoo on right arm, carrying briefcase',
   'Man in business attire seen entering parking garage, seemed to be looking for something',
   'Security camera footage shows individual matching description', 'High',
   NULL, 'https://example.com/sightings/sig002_video.mp4', 'Manual_Entry', NULL, NULL, NULL,
   NULL, 'Verified', 'High', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'security_review', 'High quality video footage available',
   'Male individual aged 35-40 years with black hair and brown eyes, standing 178cm tall and weighing 75kg, observed on August 11, 2024 at 11:30 AM at Corporate Plaza in Los Angeles. The person was wearing a dark business suit and appeared professional, with a visible tattoo on the right arm and carrying a briefcase. Security camera footage captured the individual entering a parking garage while appearing to search for something. This verified high-priority sighting has high confidence level and was documented through security review, with high-quality video footage available for analysis. The professional appearance and distinctive tattoo marking provide strong identifying characteristics for potential case matching.'),


  -- Sighting 3: Potentially matches Sarah Williams (MP003) in Boston area
  ('SIG003', 'SIGHT-2024-003', '2024-08-13', '22:15:00', '456 College Avenue', 'Boston', 'USA',
   '02116', 42.3501, -71.0689, ST_GEOGPOINT(-71.0689, 42.3501),
   'Female', '20-25', 158.0, 50.0, 'Blonde', 'Green',
   'College hoodie, jeans, appeared upset', 'Pierced ears, small mark on neck',
   'Young woman seen crying outside late-night diner, matching missing student description',
   'Diner waitress noticed distressed customer who left without ordering', 'Medium',
   'https://example.com/sightings/sig003_photo.jpg', NULL, 'Witness', 'Maria Santos', '6175552468', 'maria.santos@email.com',
   NULL, 'New', 'Medium', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'witness_report', 'Waitress has good memory for faces',
   'Female sighting aged 20-25 years with blonde hair and green eyes, approximately 158cm tall and 50kg, seen on August 13, 2024 at 10:15 PM on College Avenue in Boston. The individual was wearing a college hoodie and jeans while appearing upset, with pierced ears and a small mark visible on the neck. Witness Maria Santos, a diner waitress, observed the young woman crying outside a late-night diner, matching a missing student description. The circumstances involved a distressed customer who left without ordering, creating concern among staff. This medium-priority new sighting has medium confidence level and was reported by a witness with good facial recognition memory, potentially connecting to an active missing person case.'),


  -- Sighting 4: Does not match any current missing person
  ('SIG004', 'SIGHT-2024-004', '2024-08-14', '09:00:00', '321 Shopping Center', 'Dallas', 'USA',
   '75201', 32.7767, -96.7970, ST_GEOGPOINT(-96.7970, 32.7767),
   'Male', '40-45', 170.0, 68.0, 'Brown', 'Brown',
   'Casual clothes, baseball cap, sunglasses', 'Walked with slight limp',
   'Man seemed to be avoiding security cameras, acting suspiciously in mall',
   'Mall security noticed individual behaving oddly near electronics store', 'Low',
   NULL, 'https://example.com/sightings/sig004_video.mp4', 'Manual_Entry', NULL, NULL, NULL,
   NULL, 'New', 'Low', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'security_review', 'May not be related to any current cases',
   'Male individual aged 40-45 years with brown hair and brown eyes, approximately 170cm tall and 68kg, spotted on August 14, 2024 at 9:00 AM at a Shopping Center in Dallas. The person was wearing casual clothes, baseball cap, and sunglasses, with a noticeable slight limp while walking. Mall security noticed the individual behaving oddly and seemingly avoiding security cameras near an electronics store. The suspicious behavior and apparent camera avoidance raised security concerns, though the connection to missing person cases remains unclear. This low-priority new sighting has low confidence level and was flagged through security review, with notes indicating it may not be related to any current active cases.'),


  -- Sighting 5: Potentially matches Marcus Thompson (MP004) in San Francisco area
  ('SIG005', 'SIGHT-2024-005', '2024-08-09', '07:30:00', 'Golden Gate Park - Panhandle', 'San Francisco', 'USA',
   '94117', 37.7694, -122.4662, ST_GEOGPOINT(-122.4662, 37.7694),
   'Male', '30-35', 185.0, 80.0, 'Brown', 'Hazel',
   'Running clothes, appeared injured or disoriented', 'Visible scar on forehead, athletic build',
   'Runner seen sitting on park bench, seemed confused and asking passersby for help with directions',
   'Morning jogger stopped to offer assistance to disoriented man', 'High',
   'https://example.com/sightings/sig005_photo.jpg', NULL, 'Witness', 'Susan Martinez', '4155557891', 'susan.martinez@email.com',
   NULL, 'Under_Review', 'High', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'witness_report', 'Witness is regular jogger, knows the area well',
   'Male sighting aged 30-35 years with brown hair and hazel eyes, standing 185cm tall and weighing 80kg, observed on August 9, 2024 at 7:30 AM in Golden Gate Park Panhandle area of San Francisco. The individual was wearing running clothes and appeared injured or disoriented, with a visible scar on the forehead and athletic build. Witness Susan Martinez, a regular morning jogger, found the runner sitting on a park bench seeming confused and asking passersby for directions. The circumstances suggest potential medical distress or disorientation in a familiar jogging area. This high-priority sighting under review has high confidence level, reported by a knowledgeable local jogger who recognized unusual behavior patterns in the park environment.'),


  -- Sighting 6: Does not match any current missing person
  ('SIG006', 'SIGHT-2024-006', '2024-08-12', '14:20:00', '654 Suburban Mall', 'Phoenix', 'USA',
   '85003', 33.4384, -112.0640, ST_GEOGPOINT(-112.0640, 33.4384),
   'Female', '50-55', 162.0, 65.0, 'Gray', 'Blue',
   'Floral dress, carrying large purse', 'Wore distinctive jewelry, seemed well-dressed',
   'Well-dressed woman asking multiple people about bus schedules, seemed lost',
   'Store clerk noticed woman asking for directions repeatedly', 'Low',
   NULL, NULL, 'Witness', 'John Peterson', '6025551234', 'john.peterson@email.com',
   NULL, 'New', 'Low', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'witness_report', 'May just be tourist or confused shopper',
   'Female individual aged 50-55 years with gray hair and blue eyes, approximately 162cm tall and 65kg, seen on August 12, 2024 at 2:20 PM at Suburban Mall in Phoenix. The person was wearing a floral dress and carrying a large purse, with distinctive jewelry and well-dressed appearance. Witness John Peterson, a store clerk, noticed the woman repeatedly asking multiple people about bus schedules and appearing lost. The circumstances suggest possible confusion or disorientation rather than distress, with behavior consistent with being unfamiliar with the area. This low-priority new sighting has low confidence level for missing person connection, with witness notes indicating the individual may simply be a tourist or confused shopper rather than someone in danger.'),


  -- Sighting 7: Potentially matches Ashley Taylor (MP007) in Las Vegas area
  ('SIG007', 'SIGHT-2024-007', '2024-08-12', '02:30:00', '789 Casino Boulevard', 'Las Vegas', 'USA',
   '89102', 36.1599, -115.1398, ST_GEOGPOINT(-115.1398, 36.1599),
   'Female', '20-25', 168.0, 55.0, 'Red', 'Blue',
   'Black dress, high heels, silver jewelry', 'Freckles, multiple ear piercings, appeared intoxicated',
   'Young woman with red hair seen outside casino at 2:30 AM, seemed distressed and alone',
   'Casino security noticed individual matching description leaving property', 'Medium',
   NULL, 'https://example.com/sightings/sig007_video.mp4', 'Manual_Entry', NULL, NULL, NULL,
   NULL, 'Under_Review', 'Medium', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'security_review', 'Timeline matches missing person case timeline',
   'Female sighting aged 20-25 years with red hair and blue eyes, standing 168cm tall and weighing 55kg, observed on August 12, 2024 at 2:30 AM on Casino Boulevard in Las Vegas. The individual was wearing a black dress, high heels, and silver jewelry, with visible freckles and multiple ear piercings while appearing intoxicated. Casino security footage captured the young woman outside the casino property appearing distressed and alone during early morning hours. The circumstances align with nightlife district activity but raise concerns about safety given the late hour and apparent distress. This medium-priority sighting under review has medium confidence level, with security documentation and timeline correlation to active missing person cases.'),


  -- Sighting 8: Does not match any current missing person
  ('SIG008', 'SIGHT-2024-008', '2024-08-10', '18:45:00', '147 Riverfront Park', 'Portland', 'USA',
   '97204', 45.5152, -122.6784, ST_GEOGPOINT(-122.6784, 45.5152),
   'Male', '60-65', 175.0, 70.0, 'White', 'Gray',
   'Casual outdoor clothing, hiking boots', 'Carried walking stick, moved slowly',
   'Elderly man feeding ducks alone in park, seemed to know regular visitors',
   'Park regular noticed unfamiliar elderly visitor', 'Low',
   'https://example.com/sightings/sig008_photo.jpg', NULL, 'Witness', 'Emily Chen', '5035556789', 'emily.chen@email.com',
   NULL, 'New', 'Low', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'witness_report', 'Probably just local resident, not missing person',
   'Male individual aged 60-65 years with white hair and gray eyes, approximately 175cm tall and 70kg, spotted on August 10, 2024 at 6:45 PM at Riverfront Park in Portland. The person was wearing casual outdoor clothing and hiking boots, carrying a walking stick and moving slowly. Witness Emily Chen, a park regular, noticed the elderly man feeding ducks alone and seeming to know other regular park visitors. The circumstances suggest normal recreational activity rather than distress, with behavior consistent with local community engagement. This low-priority new sighting has low confidence level for missing person correlation, with witness assessment indicating the individual is probably a local resident engaging in routine park activities rather than someone who is missing.'),


  -- Sighting 9: Potentially matches Jessica Brown (MP009) in New York area
  ('SIG009', 'SIGHT-2024-009', '2024-08-14', '19:30:00', '258 Financial District', 'New York', 'USA',
   '10006', 40.7489, -73.9851, ST_GEOGPOINT(-73.9851, 40.7489),
   'Female', '30-35', 162.0, 58.0, 'Black', 'Brown',
   'Professional business suit, laptop bag, jewelry', 'Distinctive mole on right cheek, wedding ring',
   'Professional woman seen entering subway station, seemed to be checking phone frequently',
   'Subway station attendant noticed well-dressed woman matching description', 'High',
   NULL, 'https://example.com/sightings/sig009_video.mp4', 'Manual_Entry', NULL, NULL, NULL,
   NULL, 'Verified', 'High', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'transit_authority', 'MetroCard usage confirms timeline and location',
   'Female professional aged 30-35 years with black hair and brown eyes, standing 162cm tall and weighing 58kg, observed on August 14, 2024 at 7:30 PM in the Financial District of New York. The individual was wearing a professional business suit, carrying a laptop bag and jewelry, with a distinctive mole on the right cheek and wedding ring visible. Subway station attendant noticed the well-dressed woman entering the station while frequently checking her phone. Transit authority records confirm MetroCard usage that corroborates the timeline and location of the sighting. This verified high-priority sighting has high confidence level with official documentation, suggesting strong potential connection to active missing person cases in the professional/business community.'),


  -- Sighting 10: Potentially matches Christopher Miller (MP010) in Seattle area
  ('SIG010', 'SIGHT-2024-010', '2024-08-10', '17:15:00', '456 Bus Stop Avenue', 'Seattle', 'USA',
   '98102', 47.6162, -122.3221, ST_GEOGPOINT(-122.3221, 47.6162),
   'Male', '20-25', 175.0, 65.0, 'Blonde', 'Blue',
   'School uniform, backpack with stickers', 'Braces, some acne scarring, seemed nervous',
   'High school student seen at bus stop after school hours, appeared to be avoiding someone',
   'Bus driver remembered student who seemed anxious and kept looking around', 'Medium',
   'https://example.com/sightings/sig010_photo.jpg', NULL, 'Witness', 'Patricia Wong', '2065558147', 'patricia.wong@email.com',
   NULL, 'Under_Review', 'Medium', FALSE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   'witness_report', 'Bus driver has good memory, sees many students daily',
   'Male student aged 20-25 years with blonde hair and blue eyes, approximately 175cm tall and 65kg, seen on August 10, 2024 at 5:15 PM at Bus Stop Avenue in Seattle. The individual was wearing school uniform and carrying a backpack with stickers, with visible braces and some acne scarring while appearing nervous. Witness Patricia Wong, an experienced bus driver, remembered the student who seemed anxious and kept looking around as if avoiding someone. The circumstances suggest potential distress or fear rather than normal after-school behavior, with the student appearing to be in a heightened state of awareness. This medium-priority sighting under review has medium confidence level, reported by a reliable witness who regularly observes students and recognized unusual behavioral patterns indicating possible danger or concern.');

/* Notes about these sightings:
   - SIG001: Potential match for Emma Johnson (MP001) - similar location and description
   - SIG002: Potential match for David Chen (MP002) - business attire and tattoo match
   - SIG003: Potential match for Sarah Williams (MP003) - college student, similar appearance
   - SIG004: Does not match any current missing persons - suspicious behavior case
   - SIG005: Potential match for Marcus Thompson (MP004) - runner with scar, same park area
   - SIG006: Does not match any current missing persons - possibly confused tourist
   - SIG007: Potential match for Ashley Taylor (MP007) - similar clothing and location
   - SIG008: Does not match any current missing persons - regular park visitor
   - SIG009: Potential match for Jessica Brown (MP009) - professional woman, financial district
   - SIG010: Potential match for Christopher Miller (MP010) - high school student with braces

   The remaining 20 missing persons (MP011-MP030) have no sightings in this dataset,
   representing cases without leads or confirmed sightings. */