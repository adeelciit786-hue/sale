from sqlalchemy import text
from sales_app.db import engine


class FileManager:
    """
    DB-backed manager.
    Excel files are INPUT ONLY (uploads).
    """

    # ==================================================
    # DELETE MONTH DATA (HISTORICAL / CURRENT)
    # ==================================================
    def clear_month_data(self, month_label, data_type):
        """
        Delete all sales data for a given month + type.
        """
        with engine.begin() as conn:
            conn.execute(
                text("""
                    DELETE FROM sales_data
                    WHERE month_label = :month
                      AND data_type = :type
                """),
                {"month": month_label, "type": data_type},
            )

    # ==================================================
    # TARGETS
    # ==================================================
    def save_target_for_month(self, month_label, target_value):
        """
        Insert or update monthly target.
        """
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO monthly_targets (month_label, target)
                    VALUES (:month, :target)
                    ON CONFLICT (month_label)
                    DO UPDATE SET target = EXCLUDED.target
                """),
                {"month": month_label, "target": float(target_value)},
            )

        return True, "Target saved successfully"

    def get_target_for_month(self, month_label):
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT target
                    FROM monthly_targets
                    WHERE month_label = :month
                """),
                {"month": month_label},
            ).fetchone()

        return float(result[0]) if result else 0

    # ==================================================
    # DASHBOARD HELPERS
    # ==================================================
    def get_available_months(self, data_type=None):
        """
        Return distinct month labels, optionally filtered by type.
        """
        query = "SELECT DISTINCT month_label FROM sales_data"
        params = {}

        if data_type:
            query += " WHERE data_type = :type"
            params["type"] = data_type

        query += " ORDER BY month_label"

        with engine.begin() as conn:
            rows = conn.execute(text(query), params).fetchall()

        return [r[0] for r in rows]

    # ==================================================
    # UI DELETE HELPERS (FOR BUTTONS)
    # ==================================================
    def delete_historical_month(self, month_label):
        """
        Delete historical data for a specific month.
        """
        self.clear_month_data(month_label, "historical")

    def delete_current_month(self, month_label):
        """
        Delete current month data and its target.
        """
        with engine.begin() as conn:
            conn.execute(
                text("""
                    DELETE FROM sales_data
                    WHERE month_label = :month
                      AND data_type = 'current'
                """),
                {"month": month_label},
            )

            conn.execute(
                text("""
                    DELETE FROM monthly_targets
                    WHERE month_label = :month
                """),
                {"month": month_label},
            )
