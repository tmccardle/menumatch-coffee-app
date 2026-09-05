-- Menu history and characterization
CREATE TABLE IF NOT EXISTS public.menu_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_id uuid NOT NULL REFERENCES public.menus(id) ON DELETE CASCADE,
    version_number integer NOT NULL,
    uploaded_by uuid REFERENCES auth.users(id),
    uploaded_at timestamptz DEFAULT now(),
    raw_menu jsonb NOT NULL,
    parsed_menu jsonb,
    characterization jsonb,
    is_current boolean DEFAULT false,
    notes text,
    created_at timestamptz DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_menu_versions_menu ON menu_versions(menu_id);
CREATE INDEX IF NOT EXISTS idx_menu_versions_current ON menu_versions(is_current);

-- Soft delete helper
CREATE OR REPLACE FUNCTION soft_delete_menu_version(vid uuid) RETURNS void AS $$
    UPDATE menu_versions SET is_current = false WHERE id = vid;
$$ LANGUAGE sql;

-- Trigger to make only one version current
CREATE OR REPLACE FUNCTION set_current_version() RETURNS TRIGGER AS $$
BEGIN
    UPDATE menu_versions 
    SET is_current = false 
    WHERE menu_id = NEW.menu_id AND id != NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_current_trigger
    AFTER INSERT ON menu_versions
    FOR EACH ROW EXECUTE FUNCTION set_current_version();
