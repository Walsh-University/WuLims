BEGIN;

  -- Optional cleanup (uncomment if you want a fresh reset)
  TRUNCATE TABLE results_result RESTART IDENTITY CASCADE;
  TRUNCATE TABLE experiments_experiment RESTART IDENTITY CASCADE;
  TRUNCATE TABLE samples_sampleanalysis RESTART IDENTITY CASCADE;
  TRUNCATE TABLE samples_analysistype RESTART IDENTITY CASCADE;
  TRUNCATE TABLE samples_sample RESTART IDENTITY CASCADE;
  TRUNCATE TABLE instruments_instrument RESTART IDENTITY CASCADE;
  TRUNCATE TABLE customers_customer RESTART IDENTITY CASCADE;
  TRUNCATE TABLE projects_project RESTART IDENTITY CASCADE;

-- 2) Projects
INSERT INTO projects_project (
    id, name, description, status, start_date, completed_date, created_at
) VALUES
      (2001, 'Water Quality 2026', 'Municipal water panel', 'ACTIVE', '2026-01-10', NULL, NOW()),
      (2002, 'Soil Metals Baseline', 'Agricultural site survey', 'ACTIVE', '2026-01-22', NULL, NOW()),
      (2003, 'Legacy Batch', 'Closed historical batch', 'CLOSED', '2025-06-01', '2025-12-20', NOW())
    ON CONFLICT (id) DO NOTHING;

-- 3) Customers
INSERT INTO customers_customer (
    customer_id, customer_name, external_id, customer_type, created_at, is_active
) VALUES
      ('11111111-1111-1111-1111-111111111111', 'Springfield Utilities', 'CUST-0001', 'MUNICIPAL', NOW(), 'ACTIVE'),
      ('22222222-2222-2222-2222-222222222222', 'GreenField Farms',     'CUST-0002', 'COMMERCIAL', NOW(), 'ACTIVE'),
      ('33333333-3333-3333-3333-333333333333', 'Legacy Client',        'CUST-0003', 'GOVERNMENT', NOW(), 'INACTIVE')
    ON CONFLICT (customer_id) DO NOTHING;

-- 4) Instruments
INSERT INTO instruments_instrument (
    id, name, description, manufacturer, model, serial_number, is_active,
    last_calibration_date, last_maintenance_date, created_by_id, updated_by_id
) VALUES
      (3001, 'ICP-MS 01', 'Metals analysis system', 'Agilent', '7900', 'SN-ICP-7900-001', true,  '2026-01-05', '2026-01-20', NULL, NULL),
      (3002, 'GC-MS 02',  'Volatile organics',      'Shimadzu', 'QP2020', 'SN-GCMS-2020-002', true, '2026-01-12', '2026-01-28', NULL, NULL),
      (3003, 'pH Meter',  'Bench pH meter',         'Mettler', 'SevenExcellence', 'SN-PH-003', false, '2025-12-10', '2026-01-15', NULL, NULL)
    ON CONFLICT (id) DO NOTHING;

-- 5) Samples (UUID PK)
INSERT INTO samples_sample (
    sample_id, sample_name, project_id, client_name, filtration, preservation, received_at, status, approved_at, approved_by_id
) VALUES
      ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'WQ-Grab-001', 2001, 'Springfield Utilities', 'Done', 'Lab to do', NOW() - INTERVAL '5 days', 'RECEIVED',    NULL, NULL),
      ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'WQ-Grab-002', 2001, 'Springfield Utilities', 'Done', 'Lab to do', NOW() - INTERVAL '4 days', 'IN_PROGRESS', NULL, NULL),
      ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'Soil-Core-001', 2002, 'GreenField Farms', 'Not Needed', 'Lab to do', NOW() - INTERVAL '3 days', 'IN_REVIEW',   NULL, NULL),
      ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'Soil-Core-002', 2002, 'GreenField Farms', 'Lab to do', 'Lab to do', NOW() - INTERVAL '2 days', 'APPROVED',    NOW() - INTERVAL '1 day', NULL),
      ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'Legacy-Archive-001', 2003, 'Legacy Client', 'Done', 'Lab to do', NOW() - INTERVAL '10 days', 'REJECTED', NULL, NULL)
    ON CONFLICT (sample_id) DO NOTHING;

-- 6) Analysis Types
INSERT INTO samples_analysistype (
    analysis_type_id, code, name, description, is_active, sort_order
) VALUES
      ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'ICP_MS_METALS', 'ICP-MS Metals Panel', 'Trace metals quantification by ICP-MS', TRUE, 10),
      ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'GC_MS_VOC', 'GC-MS VOC Screen', 'Volatile organic compounds screening', TRUE, 20),
      ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'NUTRIENTS', 'Nutrients Panel', 'Nitrate, nitrite, and phosphate analysis', TRUE, 30),
      ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'PH', 'pH Measurement', 'Standard pH bench analysis', TRUE, 40),
      ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb005', 'LEGACY_QC', 'Legacy QC Recheck', 'Quality control rerun for legacy batches', FALSE, 90)
    ON CONFLICT (analysis_type_id) DO NOTHING;

-- 7) Sample Analysis Requests
INSERT INTO samples_sampleanalysis (
    sample_analysis_id, sample_id, analysis_type_id, requested_at
) VALUES
      ('cccccccc-cccc-cccc-cccc-ccccccccc001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', NOW() - INTERVAL '5 days'),
      ('cccccccc-cccc-cccc-cccc-ccccccccc002', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', NOW() - INTERVAL '5 days'),
      ('cccccccc-cccc-cccc-cccc-ccccccccc003', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', NOW() - INTERVAL '4 days'),
      ('cccccccc-cccc-cccc-cccc-ccccccccc004', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', NOW() - INTERVAL '3 days'),
      ('cccccccc-cccc-cccc-cccc-ccccccccc005', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', NOW() - INTERVAL '2 days'),
      ('cccccccc-cccc-cccc-cccc-ccccccccc006', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb005', NOW() - INTERVAL '10 days')
    ON CONFLICT (sample_analysis_id) DO NOTHING;

-- 8) Results
INSERT INTO results_result (
    id, title, description, sample_id, project_id, completed_at, status,
    approved_at, approved_by_id, rejected_at, rejected_by_id, notes
) VALUES
      (4001, 'Lead Panel A', 'Initial acquisition complete', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 2001, NOW() - INTERVAL '4 days', 'DRAFT',    NULL, NULL, NULL, NULL, 'Auto-
  ingested'),
      (4002, 'Lead Panel B', 'Processing calibration set',   'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 2001, NOW() - INTERVAL '2 days', 'IN_PROGRESS', NULL, NULL, NULL, NULL,
       'Calibration drift under review'),
      (4003, 'Nitrate Check','Ready for scientific review',  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 2002, NOW() - INTERVAL '1 day',  'IN_REVIEW',   NULL, NULL, NULL, NULL, 'Queued
  for reviewer'),
      (4004, 'Metals Final', 'Approved final report values', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 2002, NOW() - INTERVAL '1 day',  'APPROVED',    NOW() - INTERVAL '12 hours',
       NULL, NULL, NULL, 'Approved by reviewer1'),
      (4005, 'Legacy Recheck','Rejected due to QC failure',  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 2003, NOW() - INTERVAL '8 days', 'REJECTED',    NULL, NULL, NOW() - INTERVAL '7
  days', NULL, 'QC control out of bounds')
    ON CONFLICT (id) DO NOTHING;

-- 9) Experiments (note FK column name is project_id_id in this schema)
INSERT INTO experiments_experiment (
    id, name, description, status, created_at, data_file, version, project_id_id
) VALUES
      (5001, 'Run-ICP-2026-01', 'ICP method validation', 'COMPLETED', NOW() - INTERVAL '6 days', '/data/experiments/icp_20260101.csv', 'v1.0.0', 2001),
      (5002, 'Run-GCMS-2026-02', 'VOC screening batch',  'RUNNING',   NOW() - INTERVAL '1 day',  '/data/experiments/gcms_20260210.csv', 'v1.1.0', 2002),
      (5003, 'Run-Legacy-2025',  'Historical comparison', 'CREATED',  NOW() - INTERVAL '30 days', '/data/experiments/legacy_202512.csv', 'v0.9.5', 2003)
    ON CONFLICT (id) DO NOTHING;

-- Keep sequences aligned after explicit IDs
SELECT setval(pg_get_serial_sequence('projects_project', 'id'),      GREATEST((SELECT COALESCE(MAX(id),1) FROM projects_project), 1), true);
SELECT setval(pg_get_serial_sequence('instruments_instrument', 'id'),GREATEST((SELECT COALESCE(MAX(id),1) FROM instruments_instrument), 1), true);
SELECT setval(pg_get_serial_sequence('results_result', 'id'),        GREATEST((SELECT COALESCE(MAX(id),1) FROM results_result), 1), true);
SELECT setval(pg_get_serial_sequence('experiments_experiment', 'id'),GREATEST((SELECT COALESCE(MAX(id),1) FROM experiments_experiment), 1), true);

COMMIT;
