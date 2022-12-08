const path = require('path');

module.exports = {
    entry: './desparchado/static/src/js/main.js',
    output: {
        filename: 'js/main.js',
        path: path.resolve(__dirname, '../desparchado/static/dist'),
    }
}
