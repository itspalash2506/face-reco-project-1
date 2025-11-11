/*
  # Create persons table for face recognition system

  1. New Tables
    - `persons`
      - `id` (uuid, primary key) - Unique identifier
      - `name` (text, unique, not null) - Person's full name
      - `email` (text, not null) - Email address for notifications
      - `phone_number` (text, not null) - WhatsApp phone number (E.164 format)
      - `last_detected_at` (timestamptz) - Last time person was detected
      - `notification_sent` (boolean, default false) - Track if notification was sent
      - `created_at` (timestamptz, default now()) - Registration timestamp
      - `updated_at` (timestamptz, default now()) - Last update timestamp

  2. Security
    - Enable RLS on `persons` table
    - Add policy for public read access (for face recognition system)
    - Add policy for public insert access (for registration)
    - Add policy for public update access (for notification tracking)

  3. Notes
    - Phone numbers should be in E.164 format (e.g., +1234567890)
    - The system will query this table during face recognition
    - Notifications are sent via WhatsApp using Twilio API
*/

CREATE TABLE IF NOT EXISTS persons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  email text NOT NULL,
  phone_number text NOT NULL,
  last_detected_at timestamptz,
  notification_sent boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE persons ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access"
  ON persons
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public insert access"
  ON persons
  FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "Allow public update access"
  ON persons
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);
CREATE INDEX IF NOT EXISTS idx_persons_last_detected ON persons(last_detected_at);