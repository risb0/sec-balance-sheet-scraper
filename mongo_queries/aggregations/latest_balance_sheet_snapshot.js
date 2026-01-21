/**
 * Daily Commit #3
 * Build a clean balance-sheet snapshot for the latest filing
 *
 * This aggregation:
 * 1. Filters by symbol
 * 2. Sorts filings by date DESC
 * 3. Locks on latest filing using $group + $first
 * 4. Regroups rows into a structured balance sheet
 */

db.balance_sheets.aggregate([
  // 1️⃣ Filter by company
  {
    $match: {
      symbol: "AAPL"
    }
  },

  // 2️⃣ Sort filings (latest first)
  {
    $sort: {
      filing_date: -1
    }
  },

  // 3️⃣ Lock onto the latest filing
  {
    $group: {
      _id: "$label",
      doc: { $first: "$$ROOT" }
    }
  },

  // 4️⃣ Restore document shape
  {
    $replaceRoot: {
      newRoot: "$doc"
    }
  },

  // 5️⃣ Group into balance sheet structure
  {
    $group: {
      _id: {
        category: "$category",
        section: "$section",
        sub_section: "$sub_section"
      },
      items: {
        $push: {
          label: "$label",
          values: "$values",
          is_total: "$is_total"
        }
      }
    }
  },

  // 6️⃣ Sort sections for readability
  {
    $sort: {
      "_id.category": 1,
      "_id.section": 1,
      "_id.sub_section": 1
    }
  }
])
