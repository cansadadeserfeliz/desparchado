const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
// TODO: const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    entry: {
        main: './desparchado/static/src/js/main',
        dashboard: './desparchado/static/src/js/dashboard'
    },
    output: {
        filename: 'js/[name].[fullhash].js',
        path: path.resolve(__dirname, '../desparchado/static/dist'),
        clean: true,
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                exclude: /node_modules/,
                use: 'ts-loader'
            },
            {
                test: /\.s[ac]ss$/i,
                exclude: /node_modules/,
                use: [
                    // Creates `style` nodes from JS strings
                    'style-loader',
                    // TODO: MiniCssExtractPlugin.loader,
                    // Translates CSS into CommonJS
                    'css-loader',
                    // Compiles Sass to CSS
                    'sass-loader',
                ]
            },
        ]
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        //TODO: new MiniCssExtractPlugin({filename: './desparchado/static/dist/css/[name].css',})
    ],
}
