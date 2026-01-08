from __future__ import annotations

from datetime import datetime
from typing import Iterable

from playwright.async_api import async_playwright

from app.domain.money import format_currency
from app.utils.logger import get_logger

logger = get_logger("pennywise.report")


class ReportService:
    """
    Responsible ONLY for:
    - transforming transaction data into HTML
    - rendering PDF from HTML
    - styling, totals, formatting

    ❌ No DB access
    ❌ No auth
    ❌ No request objects
    """

    async def generate_transaction_report(
        self,
        *,
        user_id: str,
        transactions: Iterable[dict],
        title: str,
        period_label: str,
        output_path: str,
    ) -> str:
        """
        Generate a PDF report for given transactions using Playwright.

        Args:
            user_id: owner of the report
            transactions: iterable of transaction dicts
            title: report title (e.g. "Monthly Statement")
            period_label: "Jan 2026", "01–31 Jan 2026"
            output_path: where PDF will be written

        Returns:
            output_path
        """

        tx_list = list(transactions)

        logger.info(
            "PDF report generation started",
            extra={
                "user_id": user_id,
                "count": len(tx_list),
                "output": output_path,
            },
        )

        html = self._build_html(
            title=title,
            period_label=period_label,
            transactions=tx_list,
        )

        # -------------------------
        # Playwright PDF rendering (async)
        # -------------------------
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html)
            await page.pdf(
                path=output_path,
                format="A4",
                margin={"top":"20px","bottom": "20px", "left": "20px", "right": "20px"},
            )
            await browser.close()

        logger.info(
            "PDF report generated successfully",
            extra={
                "user_id": user_id,
                "path": output_path,
            },
        )

        return output_path

    # -------------------------------------------------
    # HTML builders
    # -------------------------------------------------
    def _build_html(
        self,
        *,
        title: str,
        period_label: str,
        transactions: list[dict],
    ) -> str:
        income_total = sum(
            t["amount"] for t in transactions if t["type"] == "income"
        )
        expense_total = sum(
            t["amount"] for t in transactions if t["type"] == "expense"
        )
        net = income_total - expense_total

        rows_html = "".join(self._render_row(t) for t in transactions)

        generated_at = datetime.utcnow().strftime("%d %b %Y %H:%M UTC")

        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                {self._base_css()}
            </style>
        </head>
        <body>

            <header>
                <h1>{title}</h1>
                <p class="period">{period_label}</p>
                <p class="generated">Generated at {generated_at}</p>
            </header>

            <section class="summary">
                <div>Income: <strong>{format_currency(income_total)}</strong></div>
                <div>Expense: <strong>{format_currency(expense_total)}</strong></div>
                <div class="net">
                    Net: <strong>{format_currency(net)}</strong>
                </div>
            </section>

            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Category</th>
                        <th>Type</th>
                        <th class="amount">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

        </body>
        </html>
        """

    def _render_row(self, t: dict) -> str:
        date = (
            t["date"].strftime("%d %b %Y")
            if hasattr(t["date"], "strftime")
            else str(t["date"])
        )

        amount_class = "income" if t["type"] == "income" else "expense"

        return f"""
        <tr>
            <td>{date}</td>
            <td>{t.get("description", "")}</td>
            <td>{t.get("category", "")}</td>
            <td>{t["type"].title()}</td>
            <td class="amount {amount_class}">
                {format_currency(t["amount"])}
            </td>
        </tr>
        """

    # -------------------------------------------------
    # CSS
    # -------------------------------------------------
    def _base_css(self) -> str:
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial;
            font-size: 12px;
            color: #222;
            margin: 24px;
        }

        header {
            margin-bottom: 24px;
        }

        h1 {
            margin: 0;
            font-size: 20px;
        }

        .period {
            color: #666;
            margin: 4px 0;
        }

        .generated {
            font-size: 10px;
            color: #999;
        }

        .summary {
            display: flex;
            gap: 24px;
            margin-bottom: 20px;
        }

        .summary .net {
            font-weight: bold;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead th {
            border-bottom: 2px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        tbody td {
            border-bottom: 1px solid #eee;
            padding: 8px;
        }

        .amount {
            text-align: right;
            white-space: nowrap;
        }

        .income {
            color: #2e7d32;
        }

        .expense {
            color: #c62828;
        }
        """
