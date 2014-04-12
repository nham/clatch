/**
 * @jsx React.DOM
 */

/*
   - LogDisplay
      - SearchBox
      - LogList
         - Log Entry
            - LogBox
            - AssociatedPageList

 */
var LogDisplay = React.createClass({
  getInitialState: function() {
      return {
          entries: []
      };
  },

  componentWillMount: function() {
    $.ajax({
      url: '/logs',
      dataType: 'json',
      success: function(data) {
          console.log('LogDisplay success');
        console.log(data);
        this.setState({entries: data['logs']});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/logs', status, err.toString());
      }.bind(this)
    });
  },

  render: function() {
    return (
      <div className="logDisplay">
        <SearchBox />
        <ul>
            <li><a href="#/">index</a></li>
            <li><a href="#/log/new">new log entry</a></li>
        </ul>
        <LogList entries={this.state.entries} />
      </div>
    );
  }
});

var SearchBox = React.createClass({
  render: function() {
    return (
      <div className="searchBox">
        <input type="text" />
      </div>
    );
  }
});


var LogList = React.createClass({
  render: function() {
      var logNodes = this.props.entries.map(function(entry) {
          return <LogEntry entry={entry} />;
      });

    return (
      <div className="logList">
          {logNodes}
      </div>
    );
  }
});

var LogEntry = React.createClass({
  render: function() {
    return (
      <div className="logEntry">
          <LogBox entry={this.props.entry} />
          <AssocPageList pages={this.props.entry.pages} />
      </div>
    );
  }
});

var LogBox = React.createClass({
  render: function() {
      var tagNodes = this.props.entry.tags.map(function(tag) {
          return <li>{tag}</li>;
      });

      var editURL = "#/log/edit/" + this.props.entry.id;

      var datetime = moment.unix(this.props.entry.ts).format("DD MMM YYYY HH:mm:ss");
    return (
      <div className="logBox">
          <div>{datetime}</div>
          <div dangerouslySetInnerHTML={{__html: this.props.entry.body}} />
          <ul className="logList">{tagNodes}</ul>
          <a href={editURL}>edit</a>
      </div>
    );
  }
});

var AssocPageList = React.createClass({
  render: function() {
      var pageNodes = [];
      if (this.props.pages !== undefined) {
          var pageNodes = this.props.pages.map(function(page) {
              return <li>{page}</li>;
          });
      }
    return (
      <div className="assocPageList">
          <ul>{pageNodes}</ul>
      </div>
    );
  }
});
