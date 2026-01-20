/*
  Query: Get all balance sheet rows for the latest filing of a given symbol
  Why this exists:
  - In MongoDB, we reshape documents instead of JOINing
  - This pattern replaces "GROUP BY symbol, MAX(filing_date)" in SQL
*/

const SYMBOL = "AAPL";

db.balance_sheets.aggregate([
  // 1. Filter documents for the symbol we care about
  {
    $match: { symbol: SYMBOL }
  },

  // 2. Sort by filing_date descending (latest first)
  {
    $sort: { filing_date: -1 }
  },

  // 3. Keep only the most recent filing
  {
    $limit: 1
  },

  // 4. Return only relevant balance sheet fields
  {
    $project: {
      _id: 0,
      symbol: 1,
      filing_date: 1,
      label: 1,
      category: 1,
      section: 1,
      sub_section: 1,
      values: 1,
      is_total: 1
    }
  }
]);
