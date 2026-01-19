// Get all balance sheet items for AAPL
db.balance_sheets.find(
  { symbol: "AAPL" },
  { label: 1, section: 1, values: 1 }
)

// Find “Other current assets” across all filings
db.balance_sheets.find({
  label: "Other current assets"
})

//Get latest filing only
db.balance_sheets.find({ symbol: "AAPL" })
  .sort({ filing_date: -1 })
  .limit(1)

// Project one year only
db.balance_sheets.find(
  { label: "Total assets" },
  { "values.2024-09-28": 1 }
)

// Count items per section
db.balance_sheets.aggregate([
  { $group: { _id: "$section", count: { $sum: 1 } } }
])