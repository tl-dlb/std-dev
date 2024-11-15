'use strict';

class Countdown extends React.Component {
  _mounted = false;
  loading  = false;
  hasError = false;

  constructor(props) {
    super(props) 
    this.state = { 
      beginTS:   this.props.biddingBegin,
      endTS:     this.props.biddingEnd,
      currentTS: Date.now(),
    }
  }

  componentDidMount() {
    this._mounted = true;
    this.fetchData();
    this.timerID = setInterval(() => this.tick(), 1000);
  }

  componentWillUnmount() {
    this._mounted = false;
    clearInterval(this.timerID);
  }

  tick() {
    this.setState({currentTS: Date.now()});
  }

  fetchData() {
    console.log('fetching countdown...');
    this.loading = true;
    fetch('/api/lot/' + this.props.lotId + '/')
      .then(res => res.json())
      .then((data) => {
        if (this._mounted) {
          console.log('setting data...');
          this.setState(
            { 
              beginTS: data.bidding_begin_unix, 
              endTS: data.bidding_end_unix, 
            }, 
            function () { this.render(); }
          );
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

  render() {
    let end     = this.state.endTS * 1000;
    let current = this.state.currentTS;

    let mainIntEnd   = (this.state.beginTS + 900) * 1000;
    let firstIntEnd  = (this.state.beginTS + 1200) * 1000;
    let secondIntEnd = (this.state.beginTS + 1500) * 1000;
    let thirdIntEnd  = (this.state.beginTS + 1800) * 1000;

    return (
      <React.Fragment>
        { mainIntEnd <= end && <div className="py-3">
                <dt className="text-sm font-medium text-gray-500">Основное время</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                  { mainIntEnd - current > 0 ? this.format(mainIntEnd - current) : '00:00:00' }
                </dd>
        </div> }

        { firstIntEnd <= end && <div className="py-3">
                <dt className="text-sm font-medium text-gray-500">Продление №1</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                  { firstIntEnd - current > 0 ? (firstIntEnd - current < 3e5 ? this.format(firstIntEnd - current) : '00:05:00') : '00:00:00' }
                </dd>
        </div> }

        { secondIntEnd <= end && <div className="py-3">
                <dt className="text-sm font-medium text-gray-500">Продление №2</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                  { secondIntEnd - current > 0 ? (secondIntEnd - current < 3e5 ? this.format(secondIntEnd - current) : '00:05:00') : '00:00:00' }
                 </dd>
        </div> }

        { thirdIntEnd <= end && <div className="py-3">
                <dt className="text-sm font-medium text-gray-500">Продление №3</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                  { thirdIntEnd - current > 0 ? (thirdIntEnd - current < 3e5 ? this.format(thirdIntEnd - current) : '00:05:00') : '00:00:00' }
                 </dd>
        </div> }

      </React.Fragment>
    );
  }

  pad(num, length = 2) {
    if ((''+num).length >= length) return num;
    var lead = '0' + new Array(length).join('0')
    return (lead + num).slice(-length);
  }

  format(millis) {
    var hour = Math.floor(millis / 36e5),
        min  = Math.floor((millis % 36e5) / 6e4),
        sec  = Math.floor((millis % 6e4) / 1000);
    hour = this.pad(hour), min = this.pad(min), sec = this.pad(sec);
    return `${hour}:${min}:${sec}`;
  }
}

