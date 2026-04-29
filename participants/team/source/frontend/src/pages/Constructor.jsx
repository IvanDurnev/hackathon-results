import MetricsGrid from '../components/dashboard/MetricsGrid';
import WorkspacePanel from '../components/dashboard/WorkspacePanel';
import { METRICS_DATA } from '../constants/dashboard';

export default function Constructor() {
  return (
    <div className="space-y-4">
      <MetricsGrid metrics={METRICS_DATA} />
      <WorkspacePanel />
    </div>
  );
}
