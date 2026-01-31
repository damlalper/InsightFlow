"""
CSV data adapter for ingestion.
"""
import csv
import io
from typing import List, Dict, Any
from decimal import Decimal, InvalidOperation


class CSVAdapter:
    """Adapter for parsing CSV marketing data."""

    REQUIRED_COLUMNS = ['campaign_id', 'platform', 'date']
    OPTIONAL_COLUMNS = [
        'campaign_name', 'ad_group_id', 'ad_group_name',
        'ad_id', 'ad_name', 'creative_url',
        'impressions', 'clicks', 'cost', 'conversions', 'revenue'
    ]

    def parse(self, csv_content: str) -> List[Dict[str, Any]]:
        """
        Parse CSV content into list of dictionaries.
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            List of parsed records
            
        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        records = []
        reader = csv.DictReader(io.StringIO(csv_content))
        
        # Validate headers
        headers = reader.fieldnames or []
        missing_required = set(self.REQUIRED_COLUMNS) - set(headers)
        if missing_required:
            raise ValueError(f"Missing required columns: {missing_required}")

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                record = self._normalize_row(row)
                records.append(record)
            except Exception as e:
                raise ValueError(f"Error parsing row {row_num}: {str(e)}")

        return records

    def _normalize_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Normalize a CSV row into standard format."""
        record = {
            'campaign_id': row['campaign_id'].strip(),
            'platform': row['platform'].strip(),
            'date': row['date'].strip(),
        }

        # Optional string fields
        if 'campaign_name' in row and row['campaign_name']:
            record['campaign_name'] = row['campaign_name'].strip()
        if 'ad_group_id' in row and row['ad_group_id']:
            record['ad_group_id'] = row['ad_group_id'].strip()
        if 'ad_group_name' in row and row['ad_group_name']:
            record['ad_group_name'] = row['ad_group_name'].strip()
        if 'ad_id' in row and row['ad_id']:
            record['ad_id'] = row['ad_id'].strip()
        if 'ad_name' in row and row['ad_name']:
            record['ad_name'] = row['ad_name'].strip()
        if 'creative_url' in row and row['creative_url']:
            record['creative_url'] = row['creative_url'].strip()

        # Numeric fields with validation
        numeric_fields = ['impressions', 'clicks', 'conversions']
        for field in numeric_fields:
            if field in row and row[field]:
                try:
                    record[field] = int(row[field])
                except ValueError:
                    record[field] = 0

        decimal_fields = ['cost', 'revenue']
        for field in decimal_fields:
            if field in row and row[field]:
                try:
                    record[field] = float(Decimal(row[field]))
                except (ValueError, InvalidOperation):
                    record[field] = 0.0

        return record
