import React from 'react';
import * as moment from 'moment';

export default function DateFormatter(props) {
    let date = moment(props.date);

    let formattedDate = date.format(props.format);

    return <span className="footer-label">{formattedDate}</span>;
}
