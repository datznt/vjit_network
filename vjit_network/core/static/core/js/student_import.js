var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        rows: window.$DATA,
        columns: [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'gender',
            'phone',
            'birth_date',
            'address',
            'school_name',
            'class_id',
            'student_code',
            'field_of_study',
            'start_year',
            'end_year'
        ],
    },
    created() {
        this.mapErrorFields = this.mapFields('errors');
        this.mapValueFields = this.mapFields('objects');
    },
    methods: {
        submitData() {

        },
        getCellClass(row, field) {
            const f = this.mapErrorFields[field];
            if (!!f) {
                return f(row, field) ? 'field-invalid' : 'field-valid';
            }
        },
        getValueOrError(row, field) {
            const fy = this.mapErrorFields[field];
            if (typeof fy == 'undefined') {
                return;
            }
            const error = fy(row, field);
            if (!!error) return error;
            const fx = this.mapValueFields[field];
            if (typeof fx == 'undefined') {
                return;
            }
            return fx(row, field);
        },
        mapFields(field) {
            return {
                'username': x => x[field].user['username'],
                'password': x => x[field].user['password'],
                'last_name': x => x[field].user['last_name'],
                'first_name': x => x[field].user['first_name'],
                'email': x => x[field].user['email'],
                'gender': x => x[field].user['gender'],
                'phone': x => x[field].student['phone'],
                'birth_date': x => x[field].student['birth_date'],
                'address': x => x[field].student['address'],
                'school_name': x => x[field].education['school_name'],
                'class_id': x => x[field].education['class_id'],
                'student_code': x => x[field].education['student_code'],
                'field_of_study': x => x[field].education['field_of_study'],
                'start_year': x => x[field].education['start_year'],
                'end_year': x => x[field].education['end_year'],
            }
        }
    }
})