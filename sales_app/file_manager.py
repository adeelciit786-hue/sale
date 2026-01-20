from sqlalchemy import text
from sales_app.db import engine


class FileManager:
    """
    DB-backed manager.
    Excel files are INPUT ONLY (uploads).
    """

    # ===============================
    # CLEAR MONTH DATA
    # ===============================
    def clear_month_data(self, month_label, data_type):
        with engine.begin() as conn:
            conn.execute(
                text("""
                DELETE FROM sales_data
                WHERE month_label = :month
                  AND data_type = :type
                """),
                {"month": month_label, "type": data_type}
            )

            conn.execute(
                text("""
                DELETE FROM uploads_log
                WHERE month_label = :month
                  AND data_type = :type
                """),
                {"month": month_label, "type": data_type}
            )

    # ===============================
    # LOG UPLOAD
    # ===============================
    def log_upload(self, month_label, data_type):
        with engine.begin() as conn:
            conn.execute(
                text("""
                INSERT INTO uploads_log (month_label, data_type)
                VALUES (:month, :type)
                """),
                {"month": month_label, "type": data_type}
            )

    # ===============================
    # TARGETS
    # ===============================
    def save_target_for_month(self, month_label, target_value):
        with engine.begin() as conn:
            conn.execute(
                text("""
                INSERT INTO targets (month_label, target_amount)
                VALUES (:month, :target)
                ON CONFLICT (month_label)
                DO UPDATE SET target_amount = EXCLUDED.target_amount
                """),
                {"month": month_label, "target": float(target_value)}
            )
        return True, "Target saved successfully"

    def get_target_for_month(self, month_label):
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                SELECT target_amount
                FROM targets
                WHERE month_label = :month
                """),
                {"month": month_label}
            ).fetchone()

        return float(result[0]) if result else 0

    # ===============================
    # DASHBOARD HELPERS
    # ===============================
    def get_available_months(self, data_type=None):
        query = "SELECT DISTINCT month_label FROM sales_data"
        params = {}

        if data_type:
            query += " WHERE data_type = :type"
            params["type"] = data_type

        query += " ORDER BY month_label"

        with engine.begin() as conn:
            rows = conn.execute(text(query), params).fetchall()

        return [r[0] for r in rows]
