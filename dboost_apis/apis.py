import os
from flask import Flask, request, json, jsonify
import dboost
from dboost import features
from dboost import cli
from dboost.utils.read import stream_tuples
from dboost.utils.printing import print_rows, debug, jsonify_rows

UPLOAD_FOLDER = 'datasets'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class DboostApiSchema:
    def __init__(self, cords=None, disabled_rules=[], discretestats=None, floats_only=False, fs=',',
                 gaussian=None, histogram=None, inmemory=False, input=None, maxrecords=1000, mixture=None,
                 partitionedhistogram=None, runtime_progress=1000, statistical=None, trainwith=None, verbosity=1):
        self.cords = cords
        self.disabled_rules = disabled_rules
        self.discretestats = discretestats
        self.floats_only = floats_only
        self.fs = fs
        self.gaussian = gaussian
        self.histogram = histogram
        self.inmemory = inmemory
        self.input = self._get_file(input)
        self.maxrecords = maxrecords
        self.mixture = mixture
        self.partitionedhistogram = partitionedhistogram
        self.runtime_progress = runtime_progress
        self.statistical = statistical
        self.trainwith = trainwith
        self.verbosity = verbosity

    def set(self, attr, value):
        if attr == 'input':
            self.input = self._get_file(value)
        else:
            setattr(self, attr, value)

    def _get_file(self, input):
        if input:
            try:
                f = open(input, 'r')
                return f
            except:
                return None
        return None


def parse_args(request, parser):
    args = DboostApiSchema()
    for k in request.json.keys():
        args.set(k, request.json[k])
    if args.input is None:
        return None, None, None, None
    models = cli.load_modules(args, parser, cli.REGISTERED_MODELS)
    analyzers = cli.load_modules(args, parser, cli.REGISTERED_ANALYZERS)

    disabled_rules = set(args.disabled_rules)
    available_rules = set(r.__name__ for rs in features.rules.values() for r in rs)
    invalid_rules = disabled_rules - available_rules
    if len(invalid_rules) > 0:
        parser.error("Unknown rule(s) {}. Known rules: {}".format(
            ", ".join(sorted(invalid_rules)),
            ", ".join(sorted(available_rules - disabled_rules))))
    rules = {t: [r for r in rs if r.__name__ not in disabled_rules]
             for t, rs in features.rules.items()}

    return args, models, analyzers, rules


@app.route('/api/datasets/upload', methods=["POST"])
def upload():
    file = request.files['file']
    filename = request.form['datasetId']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return json.dumps({'filename': filename})


@app.route('/api/outliers/detect', methods=["POST"])
def detect():
    response = None
    parser = cli.get_stdin_parser()
    args, models, analyzers, rules = parse_args(request, parser)
    if args is None:
        error = {'message': 'dataset does not exist'}
        response = jsonify(error)
        response.status_code = 400
        return response

    testset_generator = stream_tuples(args.input, args.fs, args.floats_only, args.inmemory, args.maxrecords)

    if args.trainwith == None:
        args.trainwith = args.input
        trainset_generator = testset_generator
    else:
        trainset_generator = stream_tuples(args.trainwith, args.fs, args.floats_only, args.inmemory, args.maxrecords)

    if not args.inmemory and not args.trainwith.seekable():
        parser.error("Input does not support streaming. Try using --in-memory or loading input from a file?")

    # TODO: Input should be fed to all models in one pass.
    for model in models:
        for analyzer in analyzers:
            outliers = list(dboost.outliers(trainset_generator, testset_generator,
                                            analyzer, model, rules, args.runtime_progress, args.maxrecords))
            if len(outliers) == 0:
                debug("   All clean!")
                response = dict()
                response["clean"] = True
                response = json.dumps(response)
            else:
                response = jsonify_rows(outliers, model, analyzer.hints,
                           features.descriptions(rules), args.verbosity)
                debug("   {} outliers found".format(len(outliers)))
    return response


