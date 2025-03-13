trigger_statements = {
    'game_last_updated' :
    """
    CREATE TRIGGER games_last_updated
        BEFORE UPDATE
        ON games
    BEGIN
        UPDATE games
            SET updatedatetime = strftime('%Y-%m-%d %H:%M:%S:%s', 'now', 'localtime')
            WHERE bundle_id = old.bundle_id;
    END;


