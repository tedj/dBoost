#dBoost API Reference
This API reference is organized by resource type. Each resource type has one or more methods.
##Resource types
* Datasets
* Outliers

##Datasets

Method | HTTP request | Description
-------| -------------|------------
upload | POST  /api/datasets/upload | upload a file to the datasets directory

##Outliers

Method | HTTP request | Description
-------| -------------|------------
detect | POST  /api/outliers/detect | detect outliers in a given dataset

##Datasets: upload
##Request
###HTTP request
` POST /api/datasets/upload `
###Parameters
Parameter name | Value	| Description
---------------| -------|------------
datasetId | string | the datasetId of the file to be uploaded
file | file | the dataset file in a csv format
##Response
If successful, this method returns a response body with the following structure:

`{
  "filename": string
}`

##Outliers: detect
##Request
###HTTP request
` POST /api/outliers/detect `
###Parameters
Parameter name | Value	| Description
---------------| -------|------------
input | string | the path of the input dataset (example: "datasets/synthetic/fizzbuzz")
trainwith | string | Use a separate dataset for correlation detection and model training. Default: None
fs | string | csv file seperator. Default: ","
disabled_rules | list | A list of disabled tuple expansion rules. (example: ["unix2date", "bits"]). Exapnsion rules are defined in ./dboost/features/
discretestats | list | ["max_buckets", "fundep_size"] Find correlations using discrete histograms to count occurences of subtuples. Considers subtuples of size fundep_size, histograms are only retained if their total is less than max_buckets distinct classes. (example: ["8", "2"])
cords | list | ["p", "epsilon"] Use the CORDS method to find correlated values. p is the maximum worst-case probability of incorrectly rejecting the independence hypothesis. epsilon is passed to --statistical. Recommended value for p: 0.001
statistical | string | "epsilon" Use a statistical model analyzer, reporting correlated values with a pearson r value greater than "epsilon"
histogram | list | ["peak_s", "outlier_s"]  Use a discrete histogram-based model, identifying fields that have a peaked distribution (peakiness is determined using the peak_s parameter), and reporting values that fall in classes totaling less than outlier_s of the corresponding histogram. (example: ["0.8", "0.2"])
partitionedhistogram | list | ["jmp_threshold", "peak_s", "outlier_s"] Use a partitioned histogram-based model. example ( ["5", "0.8", "0.05"])
gaussian | string | "n_stdev" Use a gaussian model, reporting values that fall more than n_stdev standard deviations away from the mean. (example: "3")
mixture | list | ["n_subpops", "threshold"] Use a gaussian mixture model, reporting values whose probability is below the threshold, as predicted by a model of the data comprised of n_subpops gaussians. (example: ["2", "0.3"])
inmemory | boolean | Load the entire dataset in memory before running. Required if input does not come from a seekable file. Default: False
maxrecords | integer | Stop processing after reading at most N records. Default: 1000
floats_only | boolean | Parse all numerical fields as floats. Default: False
verbosity | integer | The level of details to return. Default: 1

##Response

If successful, this method returns a response body with the following structure:

Parameter name | Value	| Description
---------------| -------|------------
clean  | boolean | false if the dataset contains outliers
rows | list | A list of outliers detected

Each row has the following structure:

Parameter name | Value	| Description
---------------| -------|------------
outlier | list | the outlier values
fields | list | a list describing  which values in the row caused it to be flagged as an outlier

Each field has the following structure:

Parameter name | Value	| Description
---------------| -------|------------
values | list | the values from the row that caused it to flagged as an outlier
field_ids | list | a list of fields indices
features | list | a list of tuple exansion features
msg | string | text describing why this row is flagged as outlier

Example:

`{
  "clean": false,
  "rows": [
    {
      "fields": [
        {
          "features": [
            "div 3",
            "strp"
          ],
          "msg": "   > Values (25, 'Fizz') (0, 1) do not match features ('div 3', 'strp')",
          "field_ids": [
            0,
            1
          ],
          "values": [
            25,
            "Fizz"
          ]
        },
        {
          "features": [
            "div 5",
            "strp"
          ],
          "msg": "   > Values (25, 'Fizz') (0, 1) do not match features ('div 5', 'strp')",
          "field_ids": [
            0,
            1
          ],
          "values": [
            25,
            "Fizz"
          ]
        }
      ],
      "outlier": [
        "25",
        "Fizz"
      ]
    },
    {
        ...
    }
}`
