/* Case Sightings Links Insert Script
   Creates 5 mock links between missing persons and sightings
   Based on potential matches identified in the sightings comments */

INSERT INTO `homeward.case_sightings` (
  id, missing_person_id, sighting_id, match_confidence, match_type, match_reason,
  status, confirmed, priority, requires_review, investigated,
  similarity_score, physical_match_score, temporal_match_score, geographical_match_score,
  distance_km, time_difference_hours, created_date, updated_date, created_by
) VALUES
  -- Link 1: Emma Johnson (MP001) -> SIG001 (San Francisco sighting)
  ('LINK001', 'MP001', 'SIG001', 0.85, 'Manual', 
   'Strong physical match: female, brown hair, blue eyes, small scar on left cheek. Geographic proximity to last seen location.',
   'Under_Review', FALSE, 'High', TRUE, FALSE,
   0.85, 0.90, 0.75, 0.95, 2.3, 26,
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'system_analysis'),

  -- Link 2: David Chen (MP002) -> SIG002 (Los Angeles business sighting)  
  ('LINK002', 'MP002', 'SIG002', 0.78, 'Manual',
   'Physical characteristics match: male, black hair, brown eyes, dragon tattoo on right arm. Business attire consistent with profile.',
   'Confirmed', TRUE, 'High', FALSE, TRUE,
   0.78, 0.85, 0.70, 0.80, 5.1, 22,
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'investigator_martinez'),

  -- Link 3: Sarah Williams (MP003) -> SIG003 (Boston college area sighting)
  ('LINK003', 'MP003', 'SIG003', 0.72, 'Tip',
   'College student profile match: female, blonde hair, green eyes, college hoodie. Age range and physical description align.',
   'Under_Review', FALSE, 'Medium', TRUE, FALSE,
   0.72, 0.80, 0.60, 0.85, 3.7, 25,
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'witness_report'),

  -- Link 4: Marcus Thompson (MP004) -> SIG005 (Golden Gate Park runner sighting)
  ('LINK004', 'MP004', 'SIG005', 0.92, 'AI_Analysis',
   'Excellent match: male runner with scar on forehead, athletic build, same park location. Timeline fits missing pattern.',
   'Confirmed', TRUE, 'High', FALSE, TRUE,
   0.92, 0.95, 0.85, 0.98, 0.8, 25,
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'ai_gemini_analysis'),

  -- Link 5: Ashley Taylor (MP007) -> SIG007 (Las Vegas casino sighting)
  ('LINK005', 'MP007', 'SIG007', 0.68, 'Manual',
   'Physical match: female, red hair, blue eyes, freckles with multiple ear piercings. Casino location and timeline align with case.',
   'Potential', FALSE, 'Medium', TRUE, FALSE,
   0.68, 0.75, 0.65, 0.60, 12.4, 18,
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 'case_officer_kim');

/* Notes about these links:
   - LINK001: Emma Johnson matched to San Francisco Market Street sighting - high confidence
   - LINK002: David Chen matched to Los Angeles business plaza sighting - confirmed match
   - LINK003: Sarah Williams matched to Boston college area sighting - under review
   - LINK004: Marcus Thompson matched to Golden Gate Park runner sighting - confirmed, highest confidence
   - LINK005: Ashley Taylor matched to Las Vegas casino sighting - potential match, requires investigation
   
   Confidence scores are based on:
   - Physical characteristics alignment (hair, eyes, distinguishing marks)
   - Geographic proximity to last known location
   - Timeline consistency with disappearance
   - Circumstances matching the missing person profile */