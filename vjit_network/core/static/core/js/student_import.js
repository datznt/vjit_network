const ROWS_STATUS = {
    READY: "ready",
    ERROR: "error",
    PROCESSING: "processing",
    PEDING: "pending",
    DONE: "done",
}

var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        rows: [],
        columns: ['username', 'password', 'first_name', 'last_name', 'email', 'gender', 'phone', 'birth_date', 'address', 'school_name', 'class_id', 'student_code', 'field_of_study', 'start_year', 'end_year'],
        hasError: false
    },
    created() {
        this.mapErrorFields = this.mapFields('errors');
        this.mapValueFields = this.mapFields('objects');
        this.rows = this.formatRows(window.$STUDENT_DATA);
        this.CREATION_STUDENT_URL = window.$STUDENT_URL;
        // setup axios header
        const csrftoken = this.getCookie('csrftoken');
        axios.defaults.headers.common['X-CSRFToken'] = csrftoken;
    },
    methods: {
        async submitData() {
            const rows = this.rows;
            for (let index = 0; index < rows.length; index++) {
                const row = rows[index];
                if (row.status === ROWS_STATUS.PEDING) {
                    continue;
                }
                row.status = ROWS_STATUS.PROCESSING;
                try {
                    const resp = await this.create(row);
                    if (resp.status === 201) {
                        row.status = ROWS_STATUS.DONE;
                    }
                } catch (err) {
                    row.status = ROWS_STATUS.ERROR;
                    if (!!err.response) {
                        row.serrors = err.response.data;
                    } else {
                        row.serrors = ['network error!']
                    }
                }
            }
        },
        async create(row) {
            return await axios.post(this.CREATION_STUDENT_URL, {
                user: row.objects.user,
                student: row.objects.student,
                education: row.objects.education
            })
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
            if (!!error) {
                this.hasError = true;
                row.status = ROWS_STATUS.PEDING;
                return error;
            }
            const fx = this.mapValueFields[field];
            if (typeof fx == 'undefined') {
                return;
            }
            return fx(row, field);
        },
        getStatusOfRow(row) {
            let badge = '', value = '';
            switch (row.status) {
                case ROWS_STATUS.PEDING:
                    badge = 'danger';
                    value = 'Invalid';
                    break;
                case ROWS_STATUS.PROCESSING:
                    badge = 'warning';
                    value = 'Processing';
                    break;
                case ROWS_STATUS.ERROR:
                    badge = 'danger';
                    value = 'Error';
                    break;
                case ROWS_STATUS.DONE:
                    badge = 'success';
                    value = 'Complete';
                    break;
                case ROWS_STATUS.READY:
                    badge = 'info';
                    value = 'Ready';
                    break;
            }
            return '<span class="badge ' + badge + '">' + value + '</span>';
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
        },
        formatRows(rows) {
            return (rows || []).map(row => ({
                ...row, status: ROWS_STATUS.READY
            }))
        },
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }
})