const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
//const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    entry: {
        main: './desparchado/static/src/js/main',
        dashboard: './desparchado/static/src/js/dashboard'
    },
    output: {
        filename: 'js/[name].[hash].js',
        path: path.resolve(__dirname, '../desparchado/static/dist'),
        clean: true,
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
