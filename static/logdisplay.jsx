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
  render: function() {
    return (
      <div className="logDisplay">
        <SearchBox />
        <ul>
            <li><a href="#/">index</a></li>
            <li><a href="#/log/new">new log entry</a></li>
        </ul>
        <LogList entries={this.props.entries} />
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
    return (
      <div className="logBox">
          <div>{this.props.entry.datetime}</div>
          {this.props.entry.body}
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
