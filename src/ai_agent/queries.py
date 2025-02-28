TASK_HIERARCHY_QUERY = f"""
    SELECT
        CONCAT(
            ksi_name, ' starts on ', TO_CHAR(start_date, 'YYYY-MM-DD'), ' and ends on ', end_date, '.'
            ) AS text
    FROM tasks_ksi
    WHERE status = 'not_started'
    """
