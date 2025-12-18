import { FeedbackWidget } from '@widget/components';

// Mock user - simulates what you'd get from NextAuth or BetterAuth
const mockUser = {
  id: 'user_123',
  email: 'jason@example.com',
  name: 'Jason',
};

// Airtable config - uses environment variables
// Create a .env file with your real values to test end-to-end
const airtableConfig = {
  apiKey: import.meta.env.VITE_AIRTABLE_API_KEY || 'mock_api_key',
  baseId: import.meta.env.VITE_AIRTABLE_BASE_ID || 'mock_base_id',
  tableName: import.meta.env.VITE_AIRTABLE_TABLE_NAME || 'Feedback',
};

function App() {
  return (
    <div className="app">
      <header>
        <h1>Feedback Widget Test Harness</h1>
        <p>Click the "Feedback" tab on the right edge to test the widget.</p>
      </header>

      <main>
        <section>
          <h2>Test Content</h2>
          <p>
            This page has some content to make screenshot testing more
            interesting. The widget should capture this entire page when opened.
          </p>

          <div className="card">
            <h3>Sample Card</h3>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </p>
          </div>

          <div className="card">
            <h3>Another Card</h3>
            <p>
              Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
              nisi ut aliquip ex ea commodo consequat.
            </p>
          </div>
        </section>

        <section>
          <h2>Configuration</h2>
          <table>
            <tbody>
              <tr>
                <td>User Email:</td>
                <td>{mockUser.email}</td>
              </tr>
              <tr>
                <td>User ID:</td>
                <td>{mockUser.id}</td>
              </tr>
              <tr>
                <td>Airtable Connected:</td>
                <td>
                  {import.meta.env.VITE_AIRTABLE_API_KEY
                    ? '✅ Yes (using .env)'
                    : '⚠️ No (using mock - create .env to test)'}
                </td>
              </tr>
            </tbody>
          </table>
        </section>
      </main>

      {/* The Feedback Widget */}
      <FeedbackWidget
        user={mockUser}
        appName="Test Harness"
        airtableConfig={airtableConfig}
      />
    </div>
  );
}

export default App;
