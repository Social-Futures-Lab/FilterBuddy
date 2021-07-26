# API Endpoints

## Filter (Groups)
- loadFilters()
  - Returns: A list of filters, each with their serialized representation

- loadFilter(id)
  - Given filter id, return the filter definition
    - `name`: Name of filter
    - `rules`: List of rules that comprise the filter

- createFilter(name, reference)
  - `name`: Name of the filter group
  - `reference`: How to initialize the group
    - `empty`: Make a group with no rules
    - `existing:{id}`: Copy the rules from an existing group with `{id}`
    - `template:{template}`: Pre-populate with a platform template `{template}`
  - Returns: The `id` of the newly created filter.

- updateFilter(id, updateAction, updateValue)
  - `id`: ID of the filter being modified
  - `updateAction`: The property/sub-property being updated
    - `name`: Update the name of a filter to value in `updateValue`
    - `rules:add`: Add the `updateValue` as a rule
    - `rules:remove`: Remove the rule noted by `updateValue`

- deleteFilter(id)
  - Remove the filter with ID

## Rules
- previewRule(filterGroup, rule)
  - Return comments that match rule
    - Comment id
    - Comment text
    - Matched text (list of start-end spans)
    - Comment time

- getComment(commentId)
  - Get details of comment
    - Comment text
    - Metadata

- previewFilter(id)
  - Return the comments that match a filter (see previewRule)

# Statistics
- getStats(id)
  - Return statistics for a filter group

- getRuleStats(id, rule)
  - Return statistics for a rule in a filter group
