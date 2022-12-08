const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    entry: {
        main: './desparchado/static/src/js/main',
        dashboard: './desparchado/static/src/js/dashboard'
    },
    output: {
        filename: 'js/[name].js',
        path: path.resolve(__dirname, '../desparchado/static/dist'),
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                exclude: /node_modules/,
                use: 'ts-loader'
            }
        ]
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'})
    ],
}
