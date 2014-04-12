/**
 * @jsx React.DOM
 */

var LogFormStateHolder = React.createClass({
    getInitialState: function() {
        return {
            entry: null
        };
    },

    handleFormSubmit: function(logEntry) {
        // TODO: make this alternatively POST or PUT depending on whether its edit form or new form
        console.log(logEntry);
        $.ajax({
          url: '/logs',
          contentType: 'application/json',
          type: 'POST',
          data: JSON.stringify({'body': logEntry.body, 'tags': logEntry.tags}),
          success: function(data) {
            console.log(data);
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    },

    componentWillMount: function() {
        if (this.props.id !== undefined) {
            var url = '/logs/' + this.props.id;

            $.ajax({
              url: url,
              dataType: 'json',
              success: function(data) {
                console.log(data);
                this.setState({entry: data['log']});
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(url, status, err.toString());
              }.bind(this)
            });
        }
    },

    render: function() {
        if (this.state.entry !== null) {
            return <LogForm onFormSubmit={this.handleFormSubmit} 
                            entry={this.state.entry} />;
        } else {
            return <LogForm onFormSubmit={this.handleFormSubmit} />;
        }
    }
});


var LogForm = React.createClass({
  getInitialState: function() {
    return {body: '', tags: ''};
  },

  handleSubmit: function() {
    var body = this.refs.body.getDOMNode().value;
    var tags = this.refs.tags.getDOMNode().value;
    this.props.onFormSubmit({body: body, tags: tags});

    return false; // prevents default action of the browser
  },

  handleBodyChange: function() {
    this.setState({body: event.target.body});
  },

  render: function() {
    var tags = "";
    var text = "New log entry";
    if (this.props.entry !== undefined) {
        console.log('this.props.entry is');
        console.log(this.props.entry);
        tags = this.props.entry.tags.map(function(tag) { return "#"+tag; }).join(', ');
        text = "Edit entry";
    }

    return (
      <div className="logForm">
      {text}
        <form onSubmit={this.handleSubmit}>
          <dl>
            <dt>Body:</dt>
            <dd><textarea rows="20" cols="80" value={this.state.body} ref="body"></textarea></dd>
            <dt>Tags:</dt>
            <dd><input type="text" size="50" defaultValue={tags} ref="tags" /></dd>
            <dd><input type="submit" value="Submit" /></dd>
          </dl>
        </form>
      </div>
    );
  }
});
