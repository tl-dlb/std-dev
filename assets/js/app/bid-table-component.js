'use strict';

class BidsTable extends React.Component {
  _mounted = false;
  loading  = false;
  hasError = false;

  constructor(props) {
    super(props) 
    this.state = { bids: [] }
  }

  componentDidMount() {
    this._mounted = true;
    this.fetchData();
  }

  componentWillUnmount() {
    this._mounted = false;
  }

  fetchData() {
    console.log('fetching...');
    this.loading = true;
    fetch('/api/lot/' + this.props.lotId + '/bid/')
      .then(res => res.json())
      .then((data) => {
        if (this._mounted) {
          console.log('setting data...');
          this.setState({ bids: data }, function () { this.render(); });
          this.loading = false;
        } else {
          console.log('not mounted.');
        }
      })
      .catch(err => {
        this.hasError = true;
        this.loading  = false;
      })
  }

  renderTableData() {
    const bids = this.state.bids;
    if (bids.length > 0) {
      return bids.map((bid, index) => {
        bid.sum = bid.sum ? new Intl.NumberFormat('ru-RU', { minimumFractionDigits: 2 }).format(+bid.sum) : '';
        bid.created_at = this.getFormattedDate(bid.created_at);
        return (
          <tr key={bid.id}>
            <td><span className="me-3">{bid.created_at}</span></td>
            <td>
              <span className="me-3">{bid.sum}</span>
              {bid.mine && <span className="badge badge-success me-3">моё</span>}
              {bid.best && <span className="badge badge-danger me-3">лучшее</span>}
            </td>
            {this.props.visible == 'True' && <td><span className="me-3">{bid.company_name}</span></td>}
          </tr>
        )
      });
    } else if (this._mounted) {
      return (<tr><td colSpan="3">Цены не поданы</td></tr>);
    } else {
      return (<tr><td colSpan="3">Загрузка...</td></tr>);
    }
  }

  render() {
    return (
      <div className="table-container">
        <table className="table table-striped mb-0">
          <thead>
            <tr>
              <th style={{width: '33.33%'}}>Дата подачи</th>
              <th style={{width: '33.33%'}}>Сумма</th>
              {this.props.visible == 'True' && <th style={{width: '33.33%'}}>Компания</th>}
            </tr>
          </thead>
          <tbody>
            {this.renderTableData()}
          </tbody>
        </table>
      </div>  
    );
  }

  pad(num, length) {
    if ((''+num).length >= length) return num;
    var lead = '0' + new Array(length).join('0')
    return (lead + num).slice(-length);
  }

  getFormattedDate(date) {
    const d = new Date(Date.parse(date));
    const day = this.pad(d.getDate(),2);
    const month = this.pad(d.getMonth()+1,2);
    const year = this.pad(d.getFullYear(),2);
    const hour = this.pad(d.getHours(),2);
    const minute = this.pad(d.getMinutes(),2);
    const second = this.pad(d.getSeconds(),2);
    const msec = this.pad(d.getMilliseconds(),3);
    return `${day}.${month}.${year} ${hour}:${minute}:${second}.${msec}`;
  }
}

