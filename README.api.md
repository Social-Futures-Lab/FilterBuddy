# API Endpoints

## Filter (Groups)
- loadFilters()
  - Returns: A list of filters, each with their serialized representation
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
